// Simple test to verify auto-conversation creation
console.log('Testing auto-conversation creation logic...');

// Simulate the useAppState hook behavior
let conversations = [];
let currentConversation = null;
let activeModel = { name: 'test-model' };

function createNewConversation() {
  if (!activeModel) return null;

  const newConversation = {
    id: Date.now().toString(),
    title: `New Chat - ${activeModel.name}`,
    model: activeModel.name,
    messages: [],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  conversations = [newConversation, ...conversations];
  currentConversation = newConversation;
  console.log('✅ Created new conversation:', newConversation.id);
  return newConversation;
}

function addMessage(message) {
  let conversation = currentConversation;
  
  if (!conversation) {
    conversation = createNewConversation();
    if (!conversation) return;
  }

  const updatedConversation = {
    ...conversation,
    messages: [...conversation.messages, message],
    updated_at: new Date().toISOString()
  };
  
  if (message.role === 'user' && conversation.messages.length === 0) {
    updatedConversation.title = message.content.slice(0, 50) + (message.content.length > 50 ? '...' : '');
  }
  
  currentConversation = updatedConversation;
  conversations = conversations.map(conv => 
    conv.id === conversation.id ? updatedConversation : conv
  );
  
  console.log('✅ Added message to conversation:', conversation.id);
}

function handleSendMessage(content) {
  if (!activeModel) return;
  
  let conversation = currentConversation;
  if (!conversation) {
    conversation = createNewConversation();
    if (!conversation) return;
  }

  const userMessage = {
    role: 'user',
    content,
    timestamp: new Date().toISOString()
  };
  
  addMessage(userMessage);
  console.log('✅ Message sent:', content);
}

// Test scenarios
console.log('\n--- Test 1: Send message with no conversation ---');
handleSendMessage('Hello, this should auto-create a conversation');

console.log('\n--- Test 2: Send another message to same conversation ---');
handleSendMessage('This should use the existing conversation');

console.log('\n--- Final State ---');
console.log('Conversations:', conversations.length);
console.log('Current conversation messages:', currentConversation?.messages.length);
console.log('Conversation title:', currentConversation?.title);

console.log('\n✅ Auto-conversation creation test completed!');