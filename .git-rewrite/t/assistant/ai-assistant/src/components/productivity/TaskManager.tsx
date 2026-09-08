import React, { useState } from 'react';
import { useApp } from '../../contexts/AppContext';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import { Badge } from '../ui/badge';
import { Card, CardContent } from '../ui/card';
import { ScrollArea } from '../ui/scroll-area';
import { Checkbox } from '../ui/checkbox';
import { Calendar } from '../ui/calendar';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '../ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../ui/dropdown-menu';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../ui/select';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '../ui/popover';
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  MoreVertical,
  CheckSquare,
  Calendar as CalendarIcon,
  Clock,
  AlertCircle,
  Filter
} from 'lucide-react';
import { format } from 'date-fns';
import { v4 as uuidv4 } from 'uuid';
import { Task } from '../../types';
import { cn } from '../../lib/utils';

export default function TaskManager() {
  const { state, dispatch } = useApp();
  const { tasks } = state;
  
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'pending' | 'completed'>('all');
  const [filterPriority, setFilterPriority] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [dueDate, setDueDate] = useState<Date | undefined>(undefined);

  // Filter tasks
  const filteredTasks = tasks.filter(task => {
    const matchesSearch = task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (task.description && task.description.toLowerCase().includes(searchQuery.toLowerCase()));
    
    const matchesStatus = filterStatus === 'all' || 
                         (filterStatus === 'pending' && !task.completed) ||
                         (filterStatus === 'completed' && task.completed);
    
    const matchesPriority = filterPriority === 'all' || task.priority === filterPriority;
    
    return matchesSearch && matchesStatus && matchesPriority;
  });

  // Sort tasks: incomplete first, then by priority, then by due date
  const sortedTasks = filteredTasks.sort((a, b) => {
    if (a.completed !== b.completed) {
      return a.completed ? 1 : -1;
    }
    
    const priorityOrder = { high: 3, medium: 2, low: 1 };
    if (a.priority !== b.priority) {
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    }
    
    if (a.dueDate && b.dueDate) {
      return a.dueDate.getTime() - b.dueDate.getTime();
    }
    if (a.dueDate && !b.dueDate) return -1;
    if (!a.dueDate && b.dueDate) return 1;
    
    return b.createdAt.getTime() - a.createdAt.getTime();
  });

  const resetForm = () => {
    setTitle('');
    setDescription('');
    setPriority('medium');
    setDueDate(undefined);
    setEditingTask(null);
  };

  const handleCreateTask = () => {
    if (!title.trim()) return;

    const task: Task = {
      id: uuidv4(),
      title: title.trim(),
      description: description.trim() || undefined,
      completed: false,
      priority,
      dueDate,
      createdAt: new Date(),
      updatedAt: new Date()
    };

    dispatch({ type: 'ADD_TASK', payload: task });
    resetForm();
    setIsCreateDialogOpen(false);
  };

  const handleUpdateTask = () => {
    if (!editingTask || !title.trim()) return;

    dispatch({
      type: 'UPDATE_TASK',
      payload: {
        id: editingTask.id,
        updates: {
          title: title.trim(),
          description: description.trim() || undefined,
          priority,
          dueDate
        }
      }
    });

    resetForm();
    setIsCreateDialogOpen(false);
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setTitle(task.title);
    setDescription(task.description || '');
    setPriority(task.priority);
    setDueDate(task.dueDate);
    setIsCreateDialogOpen(true);
  };

  const handleToggleTask = (taskId: string, completed: boolean) => {
    dispatch({
      type: 'UPDATE_TASK',
      payload: { id: taskId, updates: { completed } }
    });
  };

  const handleDeleteTask = (taskId: string) => {
    dispatch({ type: 'DELETE_TASK', payload: taskId });
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50 border-red-200';
      case 'medium': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const isOverdue = (task: Task) => {
    return task.dueDate && !task.completed && task.dueDate < new Date();
  };

  const pendingTasks = tasks.filter(t => !t.completed).length;
  const completedTasks = tasks.filter(t => t.completed).length;
  const overdueTasks = tasks.filter(t => isOverdue(t)).length;

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <CheckSquare className="h-6 w-6 text-primary" />
            <h1 className="text-2xl font-bold">Tasks</h1>
          </div>
          
          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button onClick={resetForm}>
                <Plus className="h-4 w-4 mr-2" />
                New Task
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>
                  {editingTask ? 'Edit Task' : 'Create New Task'}
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4">
                <Input
                  placeholder="Task title..."
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
                
                <Textarea
                  placeholder="Task description (optional)..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="min-h-[100px]"
                />
                
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Priority</label>
                    <Select value={priority} onValueChange={(value: any) => setPriority(value)}>
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low</SelectItem>
                        <SelectItem value="medium">Medium</SelectItem>
                        <SelectItem value="high">High</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Due Date</label>
                    <Popover>
                      <PopoverTrigger asChild>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !dueDate && "text-muted-foreground"
                          )}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {dueDate ? format(dueDate, 'PPP') : 'Pick a date'}
                        </Button>
                      </PopoverTrigger>
                      <PopoverContent className="w-auto p-0" align="start">
                        <Calendar
                          mode="single"
                          selected={dueDate}
                          onSelect={setDueDate}
                          initialFocus
                        />
                      </PopoverContent>
                    </Popover>
                  </div>
                </div>
                
                <div className="flex gap-2 justify-end">
                  <Button 
                    variant="outline" 
                    onClick={() => {
                      resetForm();
                      setIsCreateDialogOpen(false);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button onClick={editingTask ? handleUpdateTask : handleCreateTask}>
                    {editingTask ? 'Update' : 'Create'} Task
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-4 gap-4 mb-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{pendingTasks}</div>
            <div className="text-sm text-muted-foreground">Pending</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{completedTasks}</div>
            <div className="text-sm text-muted-foreground">Completed</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{overdueTasks}</div>
            <div className="text-sm text-muted-foreground">Overdue</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-600">{tasks.length}</div>
            <div className="text-sm text-muted-foreground">Total</div>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex gap-4">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>
          
          <Select value={filterStatus} onValueChange={(value: any) => setFilterStatus(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
            </SelectContent>
          </Select>
          
          <Select value={filterPriority} onValueChange={(value: any) => setFilterPriority(value)}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priority</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Tasks List */}
      <ScrollArea className="flex-1 p-6">
        {sortedTasks.length > 0 ? (
          <div className="space-y-3">
            {sortedTasks.map(task => (
              <Card key={task.id} className={cn(
                "transition-all",
                task.completed && "opacity-60",
                isOverdue(task) && "border-red-200 bg-red-50/50"
              )}>
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <Checkbox
                      checked={task.completed}
                      onCheckedChange={(checked) => 
                        handleToggleTask(task.id, checked as boolean)
                      }
                      className="mt-1"
                    />
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between mb-2">
                        <h3 className={cn(
                          "font-medium",
                          task.completed && "line-through text-muted-foreground"
                        )}>
                          {task.title}
                        </h3>
                        
                        <DropdownMenu>
                          <DropdownMenuTrigger asChild>
                            <Button variant="ghost" size="icon" className="h-8 w-8">
                              <MoreVertical className="h-4 w-4" />
                            </Button>
                          </DropdownMenuTrigger>
                          <DropdownMenuContent align="end">
                            <DropdownMenuItem onClick={() => handleEditTask(task)}>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                            <DropdownMenuItem 
                              onClick={() => handleDeleteTask(task.id)}
                              className="text-destructive"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          </DropdownMenuContent>
                        </DropdownMenu>
                      </div>
                      
                      {task.description && (
                        <p className="text-sm text-muted-foreground mb-3">
                          {task.description}
                        </p>
                      )}
                      
                      <div className="flex items-center gap-2 flex-wrap">
                        <Badge className={getPriorityColor(task.priority)}>
                          {task.priority} priority
                        </Badge>
                        
                        {task.dueDate && (
                          <Badge variant="outline" className={cn(
                            "flex items-center gap-1",
                            isOverdue(task) && "border-red-500 text-red-600"
                          )}>
                            {isOverdue(task) ? (
                              <AlertCircle className="h-3 w-3" />
                            ) : (
                              <Clock className="h-3 w-3" />
                            )}
                            Due {format(task.dueDate, 'MMM d')}
                          </Badge>
                        )}
                        
                        <span className="text-xs text-muted-foreground">
                          Created {format(task.createdAt, 'MMM d, yyyy')}
                        </span>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center h-64 text-center">
            <CheckSquare className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No tasks found</h3>
            <p className="text-muted-foreground mb-4">
              {searchQuery || filterStatus !== 'all' || filterPriority !== 'all'
                ? "Try adjusting your search or filter criteria"
                : "Create your first task to get started"
              }
            </p>
            {!searchQuery && filterStatus === 'all' && filterPriority === 'all' && (
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="h-4 w-4 mr-2" />
                Create Task
              </Button>
            )}
          </div>
        )}
      </ScrollArea>
    </div>
  );
}
