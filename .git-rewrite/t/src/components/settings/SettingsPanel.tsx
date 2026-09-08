import React from 'react';
import { useTheme } from 'next-themes';
import { Switch } from '../ui/switch';
import { Button } from '../ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';

const SettingsPanel: React.FC = () => {
  const { theme, setTheme } = useTheme();
  const [aiModel, setAiModel] = React.useState('default');
  const [temperature, setTemperature] = React.useState(0.7);
  const [autoSave, setAutoSave] = React.useState(true);

  return (
    <div className="container mx-auto py-8">
      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
          <CardDescription>Configure your AI assistant preferences</CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="general" className="w-full">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="ai">AI Preferences</TabsTrigger>
              <TabsTrigger value="privacy">Privacy & Security</TabsTrigger>
            </TabsList>
            
            <TabsContent value="general">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Theme</Label>
                    <p className="text-sm text-muted-foreground">Switch between light and dark mode</p>
                  </div>
                  <Select value={theme} onValueChange={setTheme}>
                    <SelectTrigger className="w-[180px]">
                      <SelectValue placeholder="Select theme" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="system">System</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Auto-save conversations</Label>
                    <p className="text-sm text-muted-foreground">Automatically save your chat history</p>
                  </div>
                  <Switch checked={autoSave} onCheckedChange={setAutoSave} />
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="ai">
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label>AI Model</Label>
                  <Select value={aiModel} onValueChange={setAiModel}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select AI model" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="default">Default Assistant</SelectItem>
                      <SelectItem value="creative">Creative Writer</SelectItem>
                      <SelectItem value="code">Code Assistant</SelectItem>
                      <SelectItem value="productivity">Productivity Coach</SelectItem>
                      <SelectItem value="research">Research Helper</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <Label>Response Creativity: {temperature}</Label>
                  </div>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={temperature}
                    onChange={(e) => setTemperature(parseFloat(e.target.value))}
                    className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
                  />
                  <p className="text-sm text-muted-foreground">
                    Lower values = more focused, higher values = more creative
                  </p>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="privacy">
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Clear chat history</Label>
                    <p className="text-sm text-muted-foreground">Remove all conversation data from this device</p>
                  </div>
                  <Button variant="outline" size="sm" className="text-red-600 hover:text-red-800">
                    Clear History
                  </Button>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="space-y-0.5">
                    <Label>Data collection</Label>
                    <p className="text-sm text-muted-foreground">Allow anonymous usage data to improve the service</p>
                  </div>
                  <Switch checked={true} />
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

export default SettingsPanel;