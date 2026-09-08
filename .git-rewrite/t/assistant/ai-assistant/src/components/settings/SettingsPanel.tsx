import React, { useContext } from 'react';
import { useApp } from '../../contexts/AppContext';
import { useTheme } from 'next-themes';
import { Button } from '../ui/button';
import { Switch } from '../ui/switch';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Slider } from '../ui/slider';
import { Badge } from '../ui/badge';
import { 
  Sun, 
  Moon, 
  Monitor, 
  Languages, 
  MessageSquare, 
  Bell, 
  Save,
  RefreshCw,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import { cn } from '../../lib/utils';

const SettingsPanel: React.FC = () => {
  const { state, dispatch } = useApp();
  const { theme, setTheme } = useTheme();
  const [localSettings, setLocalSettings] = React.useState(state.settings);
  const [activeTab, setActiveTab] = React.useState('general');
  const [showRestartDialog, setShowRestartDialog] = React.useState(false);

  // Sync local settings with global state
  React.useEffect(() => {
    setLocalSettings(state.settings);
  }, [state.settings]);

  const handleSettingChange = (key: keyof typeof localSettings, value: any) => {
    setLocalSettings(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: localSettings });
    // Show success message
    // In a real app, you might use a toast notification
    console.log('Settings saved successfully');
  };

  const handleReset = () => {
    setLocalSettings({
      theme: 'system',
      fontSize: 'medium',
      language: 'en',
      notifications: true,
      autoSave: true,
      defaultMode: 'general'
    });
  };

  const fontSizeOptions = [
    { value: 'small', label: 'Small', className: 'text-sm' },
    { value: 'medium', label: 'Medium', className: 'text-base' },
    { value: 'large', label: 'Large', className: 'text-lg' },
    { value: 'x-large', label: 'Extra Large', className: 'text-xl' }
  ];

  const languageOptions = [
    { value: 'en', label: 'English' },
    { value: 'es', label: 'Spanish' },
    { value: 'fr', label: 'French' },
    { value: 'de', label: 'German' },
    { value: 'zh', label: 'Chinese' },
    { value: 'ja', label: 'Japanese' }
  ];

  const defaultModeOptions = [
    { value: 'general', label: 'General Assistant' },
    { value: 'creative', label: 'Creative Writer' },
    { value: 'technical', label: 'Code Assistant' },
    { value: 'productivity', label: 'Productivity Coach' },
    { value: 'research', label: 'Research Helper' }
  ];

  return (
    <div className="container mx-auto py-8 px-4 max-w-4xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold">Settings</h1>
          <p className="text-muted-foreground mt-2">
            Customize your AI Assistant experience
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={handleReset}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset
          </Button>
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save Changes
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general" className="flex items-center gap-2">
            <MessageSquare className="h-4 w-4" />
            General
          </TabsTrigger>
          <TabsTrigger value="appearance" className="flex items-center gap-2">
            <Monitor className="h-4 w-4" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="notifications" className="flex items-center gap-2">
            <Bell className="h-4 w-4" />
            Notifications
          </TabsTrigger>
          <TabsTrigger value="privacy" className="flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Privacy
          </TabsTrigger>
        </TabsList>

        {/* General Settings */}
        <TabsContent value="general">
          <Card>
            <CardHeader>
              <CardTitle>General Settings</CardTitle>
              <CardDescription>
                Configure your default preferences and behavior
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Default AI Assistant</Label>
                  <p className="text-sm text-muted-foreground">
                    Choose which AI personality to use by default
                  </p>
                </div>
                <Select 
                  value={localSettings.defaultMode} 
                  onValueChange={(value) => handleSettingChange('defaultMode', value)}
                >
                  <SelectTrigger className="w-[240px]">
                    <SelectValue placeholder="Select default mode" />
                  </SelectTrigger>
                  <SelectContent>
                    {defaultModeOptions.map((mode) => (
                      <SelectItem key={mode.value} value={mode.value}>
                        {mode.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Language</Label>
                  <p className="text-sm text-muted-foreground">
                    Select your preferred language
                  </p>
                </div>
                <Select 
                  value={localSettings.language} 
                  onValueChange={(value) => handleSettingChange('language', value)}
                >
                  <SelectTrigger className="w-[240px]">
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    {languageOptions.map((lang) => (
                      <SelectItem key={lang.value} value={lang.value}>
                        {lang.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Auto-save conversations</Label>
                  <p className="text-sm text-muted-foreground">
                    Automatically save your chat history
                  </p>
                </div>
                <Switch 
                  checked={localSettings.autoSave} 
                  onCheckedChange={(checked) => handleSettingChange('autoSave', checked)} 
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Appearance Settings */}
        <TabsContent value="appearance">
          <Card>
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>
                Customize the look and feel of your assistant
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Theme</Label>
                  <p className="text-sm text-muted-foreground">
                    Choose your preferred color scheme
                  </p>
                </div>
                <Select value={theme} onValueChange={setTheme}>
                  <SelectTrigger className="w-[240px]">
                    <SelectValue placeholder="Select theme" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="light">
                      <div className="flex items-center">
                        <Sun className="h-4 w-4 mr-2" />
                        Light
                      </div>
                    </SelectItem>
                    <SelectItem value="dark">
                      <div className="flex items-center">
                        <Moon className="h-4 w-4 mr-2" />
                        Dark
                      </div>
                    </SelectItem>
                    <SelectItem value="system">
                      <div className="flex items-center">
                        <Monitor className="h-4 w-4 mr-2" />
                        System
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Font Size</Label>
                  <p className="text-sm text-muted-foreground">
                    Adjust the text size for better readability
                  </p>
                </div>
                <Select 
                  value={localSettings.fontSize} 
                  onValueChange={(value) => handleSettingChange('fontSize', value)}
                >
                  <SelectTrigger className="w-[240px]">
                    <SelectValue placeholder="Select font size" />
                  </SelectTrigger>
                  <SelectContent>
                    {fontSizeOptions.map((option) => (
                      <SelectItem key={option.value} value={option.value}>
                        <div className={option.className}>{option.label}</div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Font Size Preview</Label>
                <div className="border rounded-lg p-4 bg-muted">
                  <p className={cn(
                    "transition-all duration-200",
                    localSettings.fontSize === 'small' && 'text-sm',
                    localSettings.fontSize === 'medium' && 'text-base',
                    localSettings.fontSize === 'large' && 'text-lg',
                    localSettings.fontSize === 'x-large' && 'text-xl'
                  )}>
                    This is a preview of the {localSettings.fontSize} font size. The text will adjust based on your selection.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Notifications Settings */}
        <TabsContent value="notifications">
          <Card>
            <CardHeader>
              <CardTitle>Notifications</CardTitle>
              <CardDescription>
                Control when and how you receive notifications
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Enable notifications</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive desktop notifications for new messages
                  </p>
                </div>
                <Switch 
                  checked={localSettings.notifications} 
                  onCheckedChange={(checked) => handleSettingChange('notifications', checked)} 
                />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Notification sound</Label>
                  <p className="text-sm text-muted-foreground">
                    Play a sound when receiving notifications
                  </p>
                </div>
                <Switch disabled={!localSettings.notifications} />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Task reminders</Label>
                  <p className="text-sm text-muted-foreground">
                    Get notified about upcoming tasks and deadlines
                  </p>
                </div>
                <Switch disabled={!localSettings.notifications} />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Weekly summary</Label>
                  <p className="text-sm text-muted-foreground">
                    Receive a weekly email summary of your activity
                  </p>
                </div>
                <Switch disabled={!localSettings.notifications} />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Privacy Settings */}
        <TabsContent value="privacy">
          <Card>
            <CardHeader>
              <CardTitle>Privacy & Data</CardTitle>
              <CardDescription>
                Manage your data and privacy preferences
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Anonymous usage data</Label>
                  <p className="text-sm text-muted-foreground">
                    Help improve the service by sharing anonymous usage data
                  </p>
                </div>
                <Switch />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Personalized recommendations</Label>
                  <p className="text-sm text-muted-foreground">
                    Get personalized suggestions based on your usage patterns
                  </p>
                </div>
                <Switch />
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Chat history sync</Label>
                  <p className="text-sm text-muted-foreground">
                    Sync your chat history across all your devices
                  </p>
                </div>
                <Switch />
              </div>

              <div className="border-t pt-4">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="h-5 w-5 text-yellow-500 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="font-medium text-sm">Clear all data</h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      Remove all your conversations, notes, tasks, and settings from this device.
                    </p>
                    <Button variant="destructive" size="sm" className="mt-2">
                      Clear All Data
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Save/Reset buttons - also available at bottom for convenience */}
      <div className="flex justify-end space-x-4 mt-8 pt-6 border-t">
        <Button variant="outline" onClick={handleReset}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Reset to Defaults
        </Button>
        <Button onClick={handleSave}>
          <Save className="h-4 w-4 mr-2" />
          Save All Changes
        </Button>
      </div>

      {/* Restart Dialog - would be implemented with a proper dialog component */}
      {showRestartDialog && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-background rounded-lg p-6 max-w-md w-full">
            <div className="flex items-center space-x-3 mb-4">
              <CheckCircle2 className="h-8 w-8 text-green-500" />
              <h3 className="text-lg font-semibold">Settings Saved</h3>
            </div>
            <p className="text-muted-foreground mb-6">
              Your settings have been saved successfully. Some changes may require a restart to take effect.
            </p>
            <div className="flex justify-end space-x-3">
              <Button variant="outline" onClick={() => setShowRestartDialog(false)}>
                Later
              </Button>
              <Button onClick={() => setShowRestartDialog(false)}>
                Restart Now
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SettingsPanel;