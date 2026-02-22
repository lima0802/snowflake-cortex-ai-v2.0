# Step 4.2: Implement Integration Channels

**Phase:** 4 - Interface Layer  
**Goal:** Slack and Teams bot integrations  
**Status:** ⏳ Not Started

---

## Overview

Extend DIA to Slack and Microsoft Teams for:
- Chat-based queries in Slack/Teams
- Notifications and alerts
- Collaborative insights sharing

---

## Prerequisites

- [ ] Step 3.1-3.2: API fully functional
- [ ] Slack/Teams apps created (see setup section)

---

## Slack Integration

### Setup Slack App

1. Go to https://api.slack.com/apps
2. Create New App → From scratch
3. Add Bot Token Scopes:
   - `chat:write`
   - `app_mentions:read`
   - `im:history`
4. Install to workspace
5. Copy Bot Token to `.env` as `SLACK_BOT_TOKEN`

### File: `integrations/slack_bot.py`

```python
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import requests
import os

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))
API_URL = "http://orchestrator:8000/api/v1"

# Store session IDs by channel
channel_sessions = {}

@app.event("app_mention")
def handle_mention(event, say):
    """Handle @DIA mentions"""
    user_query = event["text"].split(">", 1)[1].strip()
    channel_id = event["channel"]
    
    # Get or create session for this channel
    session_id = channel_sessions.get(channel_id)
    
    # Query API
    response = requests.post(
        f"{API_URL}/query",
        json={"query": user_query, "session_id": session_id}
    ).json()
    
    # Update session
    channel_sessions[channel_id] = response.get("session_id")
    
    # Format response for Slack
    slack_message = format_for_slack(response)
    say(slack_message)

@app.message("help")
def handle_help(message, say):
    """Show help message"""
    help_text = """
    *DIA v2.0 - Marketing Intelligence Assistant* 📊
    
    *How to use:*
    • Mention me: `@DIA what was click rate last month?`
    • DM me directly with your questions
    
    *Sample queries:*
    • What was the click rate last month?
    • Compare ES vs SE markets
    • Why did open rate drop?
    • Predict clicks for next month
    """
    say(help_text)

def format_for_slack(response: dict) -> dict:
    """Format API response for Slack blocks"""
    blocks = []
    
    # Intent
    if "intent" in response:
        intent = response["intent"]
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"📌 *Intent:* {intent['intent']} ({intent.get('confidence', 0):.0%} confidence)"
            }
        })
    
    # Results summary
    if "results" in response and "summary" in response["results"]:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": response["results"]["summary"]
            }
        })
    
    # Insights
    if "enhanced_response" in response:
        enhanced = response["enhanced_response"]
        
        if "insights" in enhanced and enhanced["insights"]:
            insights_text = "\n".join([f"• {i}" for i in enhanced["insights"]])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*💡 Key Insights*\n{insights_text}"
                }
            })
        
        if "recommendations" in enhanced and enhanced["recommendations"]:
            rec_text = "\n".join([f"• {r}" for r in enhanced["recommendations"]])
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*🎯 Recommendations*\n{rec_text}"
                }
            })
    
    return {"blocks": blocks}

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
```

---

## Microsoft Teams Integration

### Setup Teams App

1. Install Teams Toolkit in VS Code
2. Create new bot app
3. Configure bot endpoint: `https://your-domain/api/teams/messages`
4. Add to `.env`: `TEAMS_APP_ID`, `TEAMS_APP_PASSWORD`

### File: `integrations/teams_bot.py`

```python
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import Activity, ActivityTypes
import requests

API_URL = "http://orchestrator:8000/api/v1"

class DIATeamsBot(ActivityHandler):
    def __init__(self):
        self.conversation_sessions = {}
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming messages"""
        user_query = turn_context.activity.text
        conversation_id = turn_context.activity.conversation.id
        
        # Get session for this conversation
        session_id = self.conversation_sessions.get(conversation_id)
        
        # Query API
        response = requests.post(
            f"{API_URL}/query",
            json={"query": user_query, "session_id": session_id}
        ).json()
        
        # Update session
        self.conversation_sessions[conversation_id] = response.get("session_id")
        
        # Format response
        reply = self.format_for_teams(response)
        await turn_context.send_activity(reply)
    
    def format_for_teams(self, response: dict) -> str:
        """Format API response for Teams"""
        lines = []
        
        # Intent
        if "intent" in response:
            intent = response["intent"]
            lines.append(f"**📌 Intent:** {intent['intent']}")
        
        # Results
        if "results" in response and "summary" in response["results"]:
            lines.append(f"\n{response['results']['summary']}")
        
        # Enhanced response
        if "enhanced_response" in response:
            enhanced = response["enhanced_response"]
            
            if "insights" in enhanced and enhanced["insights"]:
                lines.append("\n**💡 Key Insights**")
                for insight in enhanced["insights"]:
                    lines.append(f"- {insight}")
            
            if "recommendations" in enhanced and enhanced["recommendations"]:
                lines.append("\n**🎯 Recommendations**")
                for rec in enhanced["recommendations"]:
                    lines.append(f"- {rec}")
        
        return "\n".join(lines)
```

---

## Docker Configuration

Add to `docker-compose.yml`:

```yaml
  slack-bot:
    build:
      context: ./integrations
      dockerfile: Dockerfile.slack
    env_file:
      - .env
    depends_on:
      - orchestrator

  teams-bot:
    build:
      context: ./integrations
      dockerfile: Dockerfile.teams
    ports:
      - "3978:3978"
    env_file:
      - .env
    depends_on:
      - orchestrator
```

---

## Environment Variables

Add to `.env`:

```bash
# Slack
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_APP_TOKEN=xapp-your-app-token

# Teams
TEAMS_APP_ID=your-app-id
TEAMS_APP_PASSWORD=your-app-password
```

---

## Testing

### Slack
1. Deploy Slack bot
2. Invite bot to channel: `/invite @DIA`
3. Test: `@DIA what was click rate last month?`

### Teams
1. Deploy Teams bot
2. Add bot to Teams channel
3. Test by sending message

---

## Deliverables

- [ ] Slack bot implemented
- [ ] Teams bot implemented
- [ ] Docker containers configured
- [ ] Session management per channel/conversation
- [ ] Response formatting for each platform

---

## Success Criteria

✅ Slack bot responds to mentions and DMs  
✅ Teams bot functional in channels  
✅ Formatted responses look good  
✅ Multi-turn conversations work  

---

**Next:** [Step 5.1: Evaluation Framework](09_STEP_5.1_EVALUATION.md)  
**Estimated Time:** 2-3 days
