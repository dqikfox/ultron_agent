import { Box, List, ListItem, ListItemAvatar, Avatar, ListItemText } from "@mui/material";
import { motion, AnimatePresence } from "framer-motion";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type ChatListProps = {
  messages: Message[];
  loading: boolean;
};

const ChatList = ({ messages, loading }: ChatListProps) => {
  const listEndRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <Box className="flex-1 overflow-y-auto mb-2">
      <List dense>
        <AnimatePresence>
          {messages.map((msg, idx) => (
            <motion.div key={idx} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.15 }}>
              <ListItem alignItems="flex-start" className={msg.role === "assistant" ? "bg-white dark:bg-gray-800" : "bg-primary-100 dark:bg-primary-900"}>
                <ListItemAvatar>
                  <Avatar src={msg.role === "assistant" ? "/avatar_bot.png" : "/avatar_user.png"} />
                </ListItemAvatar>
                <ListItemText primary={msg.role === "assistant" ? "Ultron" : "You"} secondary={msg.content} />
              </ListItem>
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <Box className="flex justify-center py-2">
            {/* Loading indicator */}
          </Box>
        )}
      </List>
      <div ref={listEndRef} />
    </Box>
  );
};

export default ChatList;