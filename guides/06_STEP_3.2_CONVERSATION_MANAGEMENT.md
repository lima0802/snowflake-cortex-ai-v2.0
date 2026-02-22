# Step 3.2: Implement Conversation Management

**Phase:** 3 - Orchestration Layer  
**Goal:** Manage multi-turn conversations with context preservation  
**Status:** ⏳ Not Started

---

## Overview

Build conversation management to:
- Track sessions across multiple queries
- Preserve context and follow-up understanding
- Store conversation history
- Implement context-aware responses

---

## Prerequisites

- [ ] Step 3.1: API routes implemented
- [ ] Snowflake tables for conversation storage (Step 1.2)

---

## Implementation

### File: `orchestrator/services/conversation_manager.py`

```python
from pydantic import BaseModel
from datetime import datetime
import uuid

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime
    metadata: dict = {}

class Conversation(BaseModel):
    session_id: str
    messages: list[Message]
    context: dict = {}
    created_at: datetime
    last_updated: datetime

class ConversationManager:
    def __init__(self, snowflake_conn):
        self.conn = snowflake_conn
        self.active_sessions = {}
    
    def create_session(self) -> str:
        """Create new conversation session"""
        session_id = str(uuid.uuid4())
        conversation = Conversation(
            session_id=session_id,
            messages=[],
            created_at=datetime.utcnow(),
            last_updated=datetime.utcnow()
        )
        self.active_sessions[session_id] = conversation
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str, metadata: dict = None):
        """Add message to conversation"""
        conversation = self._get_conversation(session_id)
        
        message = Message(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
            metadata=metadata or {}
        )
        
        conversation.messages.append(message)
        conversation.last_updated = datetime.utcnow()
        
        # Persist to Snowflake
        self._persist_message(session_id, message)
    
    def get_context(self, session_id: str, window: int = 5) -> list[Message]:
        """Get recent conversation context"""
        conversation = self._get_conversation(session_id)
        return conversation.messages[-window:]
    
    def analyze_follow_up(self, session_id: str, query: str) -> dict:
        """Determine if query is a follow-up"""
        context = self.get_context(session_id)
        
        # Check for pronouns/references
        has_reference = any(word in query.lower() for word in 
                           ["it", "that", "this", "them", "those"])
        
        # Get last topic
        last_topic = self._extract_topic(context[-1].content) if context else None
        
        return {
            "is_follow_up": len(context) > 0 and has_reference,
            "previous_topic": last_topic,
            "context_messages": [m.dict() for m in context]
        }
    
    def _get_conversation(self, session_id: str) -> Conversation:
        """Retrieve or load conversation"""
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = self._load_from_db(session_id)
        return self.active_sessions[session_id]
    
    def _persist_message(self, session_id: str, message: Message):
        """Persist message to Snowflake"""
        query = f"""
        INSERT INTO conversations.message_history 
        (session_id, role, content, timestamp, metadata)
        VALUES ('{session_id}', '{message.role}', '{message.content}', 
                '{message.timestamp}', '{message.metadata}')
        """
        self.conn.execute(query)
    
    def _extract_topic(self, text: str) -> str:
        """Extract main topic from message"""
        # Use Cortex Complete to extract key entities
        pass
```

---

## Update API to Use Conversation Manager

Modify `orchestrator/api/routes/query.py`:

```python
@router.post("/query")
async def query(request: QueryRequest) -> QueryResponse:
    # Get or create session
    session_id = request.session_id or conversation_manager.create_session()
    
    # Analyze for follow-up
    follow_up_context = conversation_manager.analyze_follow_up(session_id, request.query)
    
    # Add user message
    conversation_manager.add_message(session_id, "user", request.query)
    
    # Enhance query with context if follow-up
    if follow_up_context["is_follow_up"]:
        query_with_context = _enhance_query_with_context(
            request.query, 
            follow_up_context
        )
    else:
        query_with_context = request.query
    
    # Process query...
    intent = intent_classifier.classify(query_with_context)
    # ... rest of pipeline
    
    # Add assistant response
    conversation_manager.add_message(
        session_id, 
        "assistant", 
        enhanced.dict(), 
        metadata={"intent": intent.dict()}
    )
    
    return QueryResponse(
        session_id=session_id,
        # ... rest of response
    )
```

---

## Conversation Database Schema

```sql
-- Create schema
CREATE SCHEMA IF NOT EXISTS conversations;

-- Message history table
CREATE TABLE conversations.message_history (
    message_id VARCHAR DEFAULT UUID_STRING(),
    session_id VARCHAR NOT NULL,
    role VARCHAR NOT NULL,  -- 'user' or 'assistant'
    content VARIANT NOT NULL,
    timestamp TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    metadata VARIANT,
    PRIMARY KEY (message_id)
);

-- Session metadata table
CREATE TABLE conversations.sessions (
    session_id VARCHAR PRIMARY KEY,
    created_at TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    last_updated TIMESTAMP_LTZ DEFAULT CURRENT_TIMESTAMP(),
    user_id VARCHAR,
    context VARIANT
);
```

---

## Testing

```python
def test_conversation_flow():
    manager = ConversationManager(snowflake_conn)
    
    # Create session
    session_id = manager.create_session()
    
    # User asks initial query
    manager.add_message(session_id, "user", "What was click rate last month?")
    manager.add_message(session_id, "assistant", {"click_rate": 2.5})
    
    # User asks follow-up
    follow_up = manager.analyze_follow_up(session_id, "How does that compare to ES market?")
    
    assert follow_up["is_follow_up"] == True
    assert len(follow_up["context_messages"]) > 0
```

---

## Deliverables

- [ ] ConversationManager class implemented
- [ ] Session management functional
- [ ] Message persistence to Snowflake
- [ ] Follow-up detection working
- [ ] Context extraction
- [ ] API integrated with conversation manager

---

## Success Criteria

✅ Multi-turn conversations working  
✅ Context preserved across queries  
✅ Follow-up detection accurate  
✅ Conversation history stored  

---

**Next:** [Step 4.1: Web App Implementation](07_STEP_4.1_WEB_APP.md)  
**Estimated Time:** 1-2 days
