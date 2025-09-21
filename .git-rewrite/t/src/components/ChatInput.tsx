import { Box, TextField, IconButton } from "@mui/material";
import SendIcon from "@mui/icons-material/Send";

type ChatInputProps = {
  input: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  loading: boolean;
};

const ChatInput = ({ input, onChange, onSubmit, loading }: ChatInputProps) => {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSubmit(e as any);
    }
  };

  return (
    <Box component="form" onSubmit={onSubmit} className="flex items-center gap-1">
      <TextField fullWidth multiline maxRows={4} placeholder="Ask Ultron…" value={input} onChange={onChange} onKeyDown={handleKeyDown} variant="outlined" size="small" className="bg-white dark:bg-gray-800" />
      <IconButton color="primary" disabled={loading || !input.trim()} type="submit">
        <SendIcon />
      </IconButton>
    </Box>
  );
};

export default ChatInput;