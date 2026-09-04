"""
Continuous GUI Improvement System for ULTRON
Uses NVIDIA model advice to enhance the GUI constantly
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
import json
from datetime import datetime
from typing import Dict, List, Any
import time
import logging

from ultron_project_advisor import UltronProjectAdvisor
from nvidia_nim_router import UltronNvidiaRouter

logger = logging.getLogger(__name__)

class ContinuousGUIImprover:
    """Continuous GUI improvement system using NVIDIA model feedback"""
    
    def __init__(self, master):
        """Initialize the GUI improvement system"""
        self.master = master
        self.advisor = UltronProjectAdvisor()
        self.nvidia_router = UltronNvidiaRouter()
        
        # GUI improvement tracking
        self.improvement_queue = []
        self.applied_improvements = []
        self.improvement_thread = None
        self.running = False
        
        # GUI Components
        self.setup_gui()
        
        # Start improvement system
        self.start_continuous_improvement()
        
    def setup_gui(self):
        """Set up the continuous improvement GUI"""
        
        # Main window configuration
        self.master.title("🔴 ULTRON Continuous GUI Improvement System 🔴")
        self.master.geometry("1200x800")
        self.master.configure(bg='#1a1a1a')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure dark theme
        style.configure('Dark.TFrame', background='#1a1a1a')
        style.configure('Dark.TLabel', background='#1a1a1a', foreground='#00ff00')
        style.configure('Dark.TButton', background='#2d2d2d', foreground='#00ff00')
        style.configure('Dark.TNotebook', background='#1a1a1a')
        style.configure('Dark.TNotebook.Tab', background='#2d2d2d', foreground='#00ff00')
        
        # Create main notebook
        self.notebook = ttk.Notebook(self.master, style='Dark.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.create_advisor_tab()
        self.create_improvements_tab()
        self.create_gui_preview_tab()
        self.create_settings_tab()
        
        # Status bar
        self.status_frame = ttk.Frame(self.master, style='Dark.TFrame')
        self.status_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.status_label = ttk.Label(
            self.status_frame, 
            text="🔴 System Starting...",
            style='Dark.TLabel',
            font=('Consolas', 10)
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Auto-improvement toggle
        self.auto_improve_var = tk.BooleanVar(value=True)
        self.auto_improve_check = ttk.Checkbutton(
            self.status_frame,
            text="Auto-Apply Safe Improvements",
            variable=self.auto_improve_var,
            style='Dark.TLabel'
        )
        self.auto_improve_check.pack(side=tk.RIGHT)
        
    def create_advisor_tab(self):
        """Create the NVIDIA advisor monitoring tab"""
        
        self.advisor_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.advisor_frame, text="🤖 NVIDIA Advisor")
        
        # Query status
        status_frame = ttk.LabelFrame(
            self.advisor_frame, 
            text="Advisor Status", 
            style='Dark.TFrame'
        )
        status_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.query_status = ttk.Label(
            status_frame,
            text="⏳ Waiting for first query...",
            style='Dark.TLabel',
            font=('Consolas', 10)
        )
        self.query_status.pack(pady=5)
        
        # Live advice display
        advice_frame = ttk.LabelFrame(
            self.advisor_frame,
            text="Live Advice from NVIDIA Models",
            style='Dark.TFrame'
        )
        advice_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.advice_display = scrolledtext.ScrolledText(
            advice_frame,
            bg='#0d1117',
            fg='#00ff00',
            font=('Consolas', 9),
            wrap=tk.WORD
        )
        self.advice_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self.advisor_frame, style='Dark.TFrame')
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            button_frame,
            text="🔄 Manual Query",
            command=self.manual_query,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="💾 Save Report",
            command=self.save_report,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame,
            text="🎯 Priority View",
            command=self.show_priorities,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
    def create_improvements_tab(self):
        """Create the improvements tracking tab"""
        
        self.improvements_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.improvements_frame, text="⚡ Improvements")
        
        # Improvement queue
        queue_frame = ttk.LabelFrame(
            self.improvements_frame,
            text="Improvement Queue",
            style='Dark.TFrame'
        )
        queue_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Queue list
        queue_list_frame = ttk.Frame(queue_frame, style='Dark.TFrame')
        queue_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollable listbox for improvements
        self.improvements_listbox = tk.Listbox(
            queue_list_frame,
            bg='#0d1117',
            fg='#00ff00',
            font=('Consolas', 9),
            selectmode=tk.SINGLE
        )
        self.improvements_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar for listbox
        listbox_scrollbar = ttk.Scrollbar(queue_list_frame)
        listbox_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.improvements_listbox.config(yscrollcommand=listbox_scrollbar.set)
        listbox_scrollbar.config(command=self.improvements_listbox.yview)
        
        # Improvement details
        details_frame = ttk.LabelFrame(
            self.improvements_frame,
            text="Selected Improvement Details",
            style='Dark.TFrame'
        )
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.improvement_details = scrolledtext.ScrolledText(
            details_frame,
            bg='#0d1117',
            fg='#00ff00',
            font=('Consolas', 9),
            wrap=tk.WORD,
            height=8
        )
        self.improvement_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind selection event
        self.improvements_listbox.bind('<<ListboxSelect>>', self.on_improvement_select)
        
        # Action buttons
        action_frame = ttk.Frame(self.improvements_frame, style='Dark.TFrame')
        action_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(
            action_frame,
            text="✅ Apply Selected",
            command=self.apply_selected_improvement,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="❌ Reject Selected",
            command=self.reject_selected_improvement,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            action_frame,
            text="🔄 Refresh Queue",
            command=self.refresh_improvement_queue,
            style='Dark.TButton'
        ).pack(side=tk.LEFT, padx=5)
        
    def create_gui_preview_tab(self):
        """Create GUI preview and testing tab"""
        
        self.preview_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.preview_frame, text="👁️ GUI Preview")
        
        # Preview area
        preview_label = ttk.Label(
            self.preview_frame,
            text="🔴 Live GUI Preview - Changes Applied Here 🔴",
            style='Dark.TLabel',
            font=('Consolas', 12, 'bold')
        )
        preview_label.pack(pady=10)
        
        # Demonstration area
        self.demo_frame = ttk.LabelFrame(
            self.preview_frame,
            text="Demo GUI Elements",
            style='Dark.TFrame'
        )
        self.demo_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Sample UI elements for testing improvements
        self.create_demo_elements()
        
    def create_demo_elements(self):
        """Create demonstration UI elements"""
        
        # Sample button with dynamic styling
        self.demo_button = tk.Button(
            self.demo_frame,
            text="🎯 Test Button - Click Me!",
            bg='#2d2d2d',
            fg='#00ff00',
            font=('Consolas', 11),
            command=self.demo_button_click
        )
        self.demo_button.pack(pady=10)
        
        # Sample text area
        self.demo_text = scrolledtext.ScrolledText(
            self.demo_frame,
            bg='#0d1117',
            fg='#00ff00',
            font=('Consolas', 10),
            height=10,
            wrap=tk.WORD
        )
        self.demo_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Initial demo text
        demo_content = """
🔴 ULTRON GUI IMPROVEMENT DEMO AREA 🔴

This area demonstrates live GUI improvements suggested by NVIDIA models.

Features being tested:
- Color scheme optimization for accessibility
- Font size and contrast adjustments  
- Button responsiveness and feedback
- Text readability enhancements
- Layout optimization for screen readers

Watch this area change as AI suggests improvements!
        """
        
        self.demo_text.insert(tk.END, demo_content)
        
    def demo_button_click(self):
        """Handle demo button clicks"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.demo_text.insert(tk.END, f"\n[{timestamp}] Demo button clicked! 🎯")
        self.demo_text.see(tk.END)
        
    def create_settings_tab(self):
        """Create settings and configuration tab"""
        
        self.settings_frame = ttk.Frame(self.notebook, style='Dark.TFrame')
        self.notebook.add(self.settings_frame, text="⚙️ Settings")
        
        # Improvement settings
        improvement_settings = ttk.LabelFrame(
            self.settings_frame,
            text="Improvement Settings",
            style='Dark.TFrame'
        )
        improvement_settings.pack(fill=tk.X, padx=10, pady=10)
        
        # Query interval
        ttk.Label(
            improvement_settings,
            text="Query Interval (seconds):",
            style='Dark.TLabel'
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.query_interval = tk.StringVar(value="300")
        ttk.Entry(
            improvement_settings,
            textvariable=self.query_interval,
            width=10
        ).grid(row=0, column=1, padx=5, pady=5)
        
        # Focus areas
        ttk.Label(
            improvement_settings,
            text="Focus Areas:",
            style='Dark.TLabel'
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.focus_areas = tk.Text(
            improvement_settings,
            height=4,
            width=50,
            bg='#0d1117',
            fg='#00ff00',
            font=('Consolas', 9)
        )
        self.focus_areas.grid(row=1, column=1, padx=5, pady=5)
        self.focus_areas.insert(tk.END, "accessibility_enhancements\ngui_responsiveness\nuser_experience\nperformance_optimization")
        
    def start_continuous_improvement(self):
        """Start the continuous improvement process"""
        
        if not self.running:
            self.running = True
            self.improvement_thread = threading.Thread(
                target=self._improvement_loop,
                daemon=True
            )
            self.improvement_thread.start()
            
            self.update_status("🔴 Continuous improvement started")
    
    def _improvement_loop(self):
        """Main improvement loop (runs in separate thread)"""
        
        while self.running:
            try:
                # Get improvement advice from NVIDIA
                asyncio.run(self._get_improvement_advice())
                
                # Process improvement queue
                self._process_improvement_queue()
                
                # Update GUI
                self.master.after(0, self._update_gui_displays)
                
                # Wait for next cycle
                time.sleep(int(self.query_interval.get()))
                
            except Exception as e:
                logger.error(f"Error in improvement loop: {e}")
                self.master.after(0, lambda: self.update_status(f"❌ Error: {str(e)[:50]}"))
                time.sleep(60)  # Wait before retry
    
    async def _get_improvement_advice(self):
        """Get improvement advice from NVIDIA models"""
        
        try:
            # Focus on GUI-specific improvements
            gui_query = """
            Based on the ULTRON Agent accessibility GUI, suggest specific improvements for:
            1. Color contrast and accessibility compliance
            2. Button and widget responsiveness  
            3. Text readability and font optimization
            4. Layout improvements for screen readers
            5. Voice integration visual feedback
            
            Provide actionable, specific suggestions that can be implemented in tkinter.
            """
            
            # Query NVIDIA model
            response = await self.advisor.nvidia_router.ask_nvidia_async(
                gui_query,
                max_tokens=512,
                temperature=0.6
            )
            
            # Parse and queue improvements
            improvement = {
                "timestamp": datetime.now().isoformat(),
                "type": "gui_enhancement",
                "source": "nvidia_model",
                "content": response,
                "priority": "medium",
                "applied": False
            }
            
            self.improvement_queue.append(improvement)
            
            # Update live display
            self.master.after(0, lambda: self._display_new_advice(response))
            
        except Exception as e:
            logger.error(f"Error getting improvement advice: {e}")
    
    def _display_new_advice(self, advice):
        """Display new advice in the GUI"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.advice_display.insert(tk.END, f"\n[{timestamp}] 🤖 NVIDIA ADVICE:\n")
        self.advice_display.insert(tk.END, f"{advice}\n")
        self.advice_display.insert(tk.END, "-" * 50 + "\n")
        self.advice_display.see(tk.END)
        
    def _process_improvement_queue(self):
        """Process queued improvements"""
        
        if self.auto_improve_var.get():
            # Auto-apply safe improvements
            for improvement in self.improvement_queue:
                if not improvement.get("applied", False):
                    if self._is_safe_improvement(improvement):
                        self._apply_improvement(improvement)
                        improvement["applied"] = True
                        self.applied_improvements.append(improvement)
    
    def _is_safe_improvement(self, improvement):
        """Check if an improvement is safe to auto-apply"""
        
        safe_keywords = [
            "color contrast",
            "font size",
            "accessibility",
            "text readability",
            "button feedback",
            "visual indicator"
        ]
        
        content = improvement.get("content", "").lower()
        return any(keyword in content for keyword in safe_keywords)
    
    def _apply_improvement(self, improvement):
        """Apply a specific improvement to the GUI"""
        
        # Example implementations - in real system, this would be more sophisticated
        content = improvement.get("content", "").lower()
        
        if "color contrast" in content:
            # Improve color contrast
            self.demo_button.configure(bg='#0066cc', fg='#ffffff')
            
        elif "font size" in content:
            # Increase font size for better readability
            current_font = self.demo_text.cget("font")
            if isinstance(current_font, tuple) and len(current_font) >= 2:
                new_size = min(current_font[1] + 1, 14)  # Cap at 14
                self.demo_text.configure(font=(current_font[0], new_size))
                
        elif "button feedback" in content:
            # Add hover effect to buttons
            self.demo_button.configure(activebackground='#0088ff', activeforeground='#ffffff')
            
        # Log the improvement
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.demo_text.insert(tk.END, f"\n[{timestamp}] ✅ Applied improvement: {improvement.get('type', 'unknown')}")
        self.demo_text.see(tk.END)
    
    def _update_gui_displays(self):
        """Update GUI displays with current data"""
        
        # Update improvements list
        self.improvements_listbox.delete(0, tk.END)
        for i, improvement in enumerate(self.improvement_queue):
            status = "✅" if improvement.get("applied", False) else "⏳"
            priority = improvement.get("priority", "medium")
            timestamp = improvement.get("timestamp", "")[:16]  # Show date/time
            
            display_text = f"{status} [{priority.upper()}] {timestamp} - {improvement.get('type', 'improvement')}"
            self.improvements_listbox.insert(tk.END, display_text)
        
        # Update status
        total_improvements = len(self.improvement_queue)
        applied_count = sum(1 for imp in self.improvement_queue if imp.get("applied", False))
        
        self.update_status(f"🔴 Active | {total_improvements} suggestions | {applied_count} applied")
    
    def update_status(self, message):
        """Update the status display"""
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_label.configure(text=f"[{timestamp}] {message}")
        
    def manual_query(self):
        """Manually trigger a query to NVIDIA models"""
        
        # Run in thread to avoid blocking GUI
        threading.Thread(
            target=lambda: asyncio.run(self._get_improvement_advice()),
            daemon=True
        ).start()
        
        self.update_status("🔄 Manual query initiated...")
        
    def save_report(self):
        """Save improvement report to file"""
        
        report = self.advisor.generate_improvement_report()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"gui_improvement_report_{timestamp}.md"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(report)
            
            messagebox.showinfo("Report Saved", f"Improvement report saved to {filename}")
            self.update_status(f"📄 Report saved: {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")
            
    def show_priorities(self):
        """Show priority improvements in popup"""
        
        priorities = self.advisor.get_top_priorities()
        
        if not priorities:
            messagebox.showinfo("No Priorities", "No priority improvements available yet.")
            return
        
        # Create priority window
        priority_window = tk.Toplevel(self.master)
        priority_window.title("🎯 Priority Improvements")
        priority_window.geometry("800x600")
        priority_window.configure(bg='#1a1a1a')
        
        priority_text = scrolledtext.ScrolledText(
            priority_window,
            bg='#0d1117',
            fg='#00ff00',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        priority_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display priorities
        priority_text.insert(tk.END, "🎯 TOP PRIORITY IMPROVEMENTS\n")
        priority_text.insert(tk.END, "=" * 50 + "\n\n")
        
        for i, priority in enumerate(priorities, 1):
            priority_text.insert(tk.END, f"{i}. {priority['area'].replace('_', ' ').title()}\n")
            priority_text.insert(tk.END, f"Model: {priority['model'].upper()}\n")
            priority_text.insert(tk.END, f"Response: {priority['response']}\n")
            priority_text.insert(tk.END, "-" * 40 + "\n\n")
    
    def on_improvement_select(self, event):
        """Handle improvement selection"""
        
        selection = self.improvements_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.improvement_queue):
                improvement = self.improvement_queue[index]
                
                # Display details
                self.improvement_details.delete(1.0, tk.END)
                
                details = f"""Type: {improvement.get('type', 'Unknown')}
Priority: {improvement.get('priority', 'Medium')}
Source: {improvement.get('source', 'Unknown')}
Timestamp: {improvement.get('timestamp', 'Unknown')}
Applied: {'✅ Yes' if improvement.get('applied', False) else '❌ No'}

Content:
{improvement.get('content', 'No content available')}
"""
                
                self.improvement_details.insert(tk.END, details)
    
    def apply_selected_improvement(self):
        """Apply the selected improvement"""
        
        selection = self.improvements_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.improvement_queue):
                improvement = self.improvement_queue[index]
                
                if not improvement.get("applied", False):
                    self._apply_improvement(improvement)
                    improvement["applied"] = True
                    self.applied_improvements.append(improvement)
                    
                    self.update_status(f"✅ Applied improvement: {improvement.get('type', 'unknown')}")
                    self._update_gui_displays()
                else:
                    messagebox.showinfo("Already Applied", "This improvement has already been applied.")
    
    def reject_selected_improvement(self):
        """Reject the selected improvement"""
        
        selection = self.improvements_listbox.curselection()
        if selection:
            index = selection[0]
            if index < len(self.improvement_queue):
                improvement = self.improvement_queue[index]
                improvement["applied"] = True  # Mark as processed
                improvement["rejected"] = True
                
                self.update_status(f"❌ Rejected improvement: {improvement.get('type', 'unknown')}")
                self._update_gui_displays()
    
    def refresh_improvement_queue(self):
        """Refresh the improvement queue display"""
        
        self._update_gui_displays()
        self.update_status("🔄 Improvement queue refreshed")
    
    def stop_improvement(self):
        """Stop the continuous improvement process"""
        
        self.running = False
        if self.improvement_thread:
            self.improvement_thread.join(timeout=5)
        
        self.update_status("🛑 Continuous improvement stopped")


def main():
    """Main function to run the continuous GUI improver"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create main window
    root = tk.Tk()
    
    # Create and run the improver
    improver = ContinuousGUIImprover(root)
    
    # Handle window close
    def on_closing():
        improver.stop_improvement()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    print("🔴 Starting ULTRON Continuous GUI Improvement System...")
    root.mainloop()


if __name__ == "__main__":
    main()
