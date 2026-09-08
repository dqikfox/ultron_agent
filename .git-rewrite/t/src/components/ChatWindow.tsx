const OS = process.platform === 'darwin' ? 'macOS' : 'Windows';
const operatingSystem = OS;

import { Box } from "@mui/material";

function App() {
  return (
    <Box
      sx={{
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#f0f0f0"
      }}
    >
      <p>Operating System: {operatingSystem}</p>
    </Box>
  );
}

export default App;
import ChatHeader from "./ChatHeader";
import ChatList from "./ChatList";
import ChatInput from "./ChatInput";
import api from "../api/client";

type Message = {
  role: "user" | "assistant";
  content: string;
};

const ChatWindow = () => {
  const [messages, setMessages] = React.useState<Message[]>([]);
  const [input, setInput] = React.useState("");
  const [loading, setLoading] = React.useState(false);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMsg: Message = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const payload = { message: input, system_prompt: localStorage.getItem("ultron_system_prompt") ?? "" };
      const response = await api.post("/chat", payload);

      if (response.status === 200) {
        const reply = response.data.reply ?? "…";
        setMessages((prev) => [...prev, { role: "assistant", content: reply }]);
      } else {
        throw new Error(`Failed to retrieve response: ${response.statusText}`);
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [...prev, { role: "assistant", content: "⚠️ An error occurred while processing your request." }]);
    } finally {
      setLoading(false);
      setInput("");
    }
  };

  return (
    <Box className="flex flex-col h-screen max-w-2xl mx-auto bg-gray-50 dark:bg-gray-900" sx={{ p: 2 }}>
      <ChatHeader />
      <ChatList messages={messages} loading={loading} />
      <ChatInput input={input} onChange={(e) => setInput(e.target.value)} onSubmit={handleSubmit} loading={loading} />
    </Box>
  );
};

export default ChatWindow;
