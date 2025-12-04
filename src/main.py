"""
main.py
Provides the GUI for the distributed social messenger and runs the client when executed
"""

import tkinter as tk
from tkinter import ttk, filedialog
from profile import Profile

# Replace with valid DSU server address
DSU_SERVER_ADD = "YOUR SERVER ADDRESS HERE"

class Body(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the body portion of the root frame.
    """
    def __init__(self, root, select_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._select_callback = select_callback

        # List of all recipients available in the active DSU file
        self._recipients = []
        
        # After all initialization is complete, call _draw to pack the widgets into the Body instance 
        self._draw()
    
    def node_select(self, event):
        """
        Selects a node of the contact tree, binding the current recipient to that node.
        """
        selection = self.contact_tree.selection()
        if not selection:
           return
        index = int(selection[0])
        self.recipient = self._recipients[index]
    
    def get_text_entry(self) -> str:
        """
        Returns the text that is currently displayed in the entry_editor widget.
        """
        return self.entry_editor.get('1.0', 'end').rstrip()

    def set_text_entry(self, text:str):
        """
        Sets the text to be displayed in the entry_editor widget.
        """
        self.entry_editor.delete(0.0, 'end')	# delete between two indices, 0-based
        self.entry_editor.insert(0.0, text)		# insert new text at a given index
	
    def set_message_text(self, text: str):
	    """
		Sets the texts to be displayed in the message_box widget.
		"""
	    self.message_box.configure(state=tk.NORMAL)
	    self.message_box.delete(0.0, 'end')      # delete between two indices, 0-based
	    self.message_box.insert(0.0, text)       # insert new text at a given index
	    self.message_box.configure(state=tk.DISABLED)
    
    def set_contacts(self, contact:list):
        """
        Populates the self._recipients attribute with recipients from the active DSU file.
        """
        self._recipients = contact
        for id in range(0, len(self._recipients)):
            self._insert_contact_tree(id, self._recipients[id])

    def insert_contact(self, recipient):
        """
        Inserts a single contact to the contact_tree widget.
        """
        self._recipients.append(recipient)
        id = len(self._recipients) - 1 #adjust id for 0-base of treeview widget
        self._insert_contact_tree(id, recipient)

    def reset_ui(self):
        """
        Resets all UI widgets to their default state. Useful for when clearing the UI is necessary such
        as when a new DSU file is loaded.
        """
        self.set_text_entry("")
        self._posts = []
        for item in self.contact_tree.get_children():
            self.contact_tree.delete(item)

    def _insert_contact_tree(self, id, recipient):
        """
        Inserts a contact into the contact_tree widget.
        """
        # Use the first 24 characters of a post entry as the identifier in the post_tree widget
        if len(recipient) > 25:
            recipient = recipient[:24] + "..."
        self.contact_tree.insert('', id, id, text=recipient)
    
    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        contacts_frame = tk.Frame(master=self, width=150)
        contacts_frame.pack(fill=tk.BOTH, side=tk.LEFT)
        self.contact_tree = ttk.Treeview(contacts_frame)
        self.contact_tree.bind("<<TreeviewSelect>>", self.node_select)
        self.contact_tree.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=5, pady=5)

        entry_frame = tk.Frame(master=self)
        entry_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        msg_frame = tk.Frame(master=entry_frame)
        msg_frame.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=(5,10), pady=5)

        editor_frame = tk.Frame(master=entry_frame)
        editor_frame.pack(fill=tk.X, side=tk.BOTTOM, expand=False, padx=(5,20), pady=5)

        scroll_frame = tk.Frame(master=msg_frame, width=10)
        scroll_frame.pack(fill=tk.BOTH, side=tk.RIGHT, expand=False)

        self.message_box = tk.Text(msg_frame, width=0, height=10, state=tk.DISABLED)
        self.message_box.pack(fill=tk.BOTH, side=tk.TOP, expand=True, padx=0, pady=0)

        self.entry_editor = tk.Text(editor_frame, width=0, height=5)
        self.entry_editor.pack(fill=tk.X, expand=True, padx=0, pady=0)

        msg_box_scrollbar = tk.Scrollbar(master=scroll_frame, command=self.message_box.yview)
        self.message_box['yscrollcommand'] = msg_box_scrollbar.set
        msg_box_scrollbar.pack(fill=tk.Y, side=tk.LEFT, expand=False, padx=0, pady=0)


class Footer(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the footer portion of the root frame.
    """
    def __init__(self, root, save_callback=None):
        tk.Frame.__init__(self, root)
        self.root = root
        self._save_callback = save_callback
        # After all initialization is complete, call _draw to pack the widgets into the Footer instance
        self._draw()
    
    def save_click(self):
        """
        Calls the callback function specified in the save_callback class attribute, if
        available, when the save_button has been clicked.
        """
        if self._save_callback is not None:
            self._save_callback()

    def set_status(self, message):
        """
        Updates the text that is displayed in the footer_label widget
        """
        self.footer_label.configure(text=message)
    
    def _draw(self):
        """
        Call only once upon initialization to add widgets to the frame
        """
        save_button = tk.Button(master=self, text="Send", width=20)
        save_button.configure(command=self.save_click)
        save_button.pack(fill=tk.BOTH, side=tk.RIGHT, padx=(5,20), pady=5)

        self.footer_label = tk.Label(master=self, text="No file loaded. Open or create a file to continue.")
        self.footer_label.pack(fill=tk.BOTH, side=tk.LEFT, padx=5)

class MainApp(tk.Frame):
    """
    A subclass of tk.Frame that is responsible for drawing all of the widgets
    in the main portion of the root frame. Also manages all method calls for
    the Profile class.
    """
    def __init__(self, root):
        tk.Frame.__init__(self, root)
        self.root = root
        # Initialize a new Profile and assign it to a class attribute
        self._current_profile = Profile()
        self._profile_filename = None
        # After all initialization is complete, call _draw to pack the widgets into the root frame
        self._draw()

    def new_profile(self):
        """
        Creates a new DSU file when the 'New' menu item is clicked.
        """
        try:
            username = tk.simpledialog.askstring("New Profile", "Enter username:")
            if not username:
              return
            pwd = tk.simpledialog.askstring("New Profile", prompt="Enter a password:")
            if not pwd:
              return
            filename = tk.filedialog.asksaveasfile(filetypes=[('Distributed Social Profile', '*.dsu')])
            if not filename:
              return
            self._profile_filename = filename.name
            self._current_profile = Profile()
            self._current_profile.dsuserver = DSU_SERVER_ADD
            self._current_profile.username = username
            self._current_profile.password = pwd
            self._current_profile.save_profile(self._profile_filename)
            self.footer.set_status(f"{self._current_profile.username} - Ready")
            self.body.reset_ui()
        except AttributeError:
            error = "ERROR: No file loaded. Open or create a file to continue."
            print(error)
            self.footer.set_status(error)
    
    def open_profile(self):
        """
        Opens an existing DSU file when the 'Open' menu item is clicked and loads the profile
        data into the UI.
        """
        try:
            filename = tk.filedialog.askopenfile(filetypes=[('Distributed Social Profile', '*.dsu')])
            self._profile_filename = filename.name
            self._current_profile = Profile()
            self._current_profile.load_profile(self._profile_filename)

            self.footer.set_status(f"{self._current_profile.username} - Ready")
            self.body.reset_ui()
            self.body.set_contacts(self._current_profile._recipients)
        except AttributeError:
            error = "ERROR: No file loaded. Open or create a file to continue."
            print(error)
            self.footer.set_status(error)
    
    def close(self):
        """
        Closes the program when the 'Close' menu item is clicked.
        """
        self.root.destroy()

    def set_message_box(self):
        """
        Creates a text string populated with the retrieved msgs to the server.
        Calls the set_message_text method to make it appear in the text editor.
        """
        text = ""
        for msg in self._current_profile._retrievedmsgs:
            if 'recipient' in msg.keys():
                if msg['recipient'] == self.body.recipient:
                    entry = msg['message']
                    text += f'YOU: {entry}\n'   #'YOU' indicates who is sending the msg
            if 'from' in msg.keys():
                if msg['from'] == self.body.recipient:
                    entry = msg['message']
                    who = msg['from'].upper()
                    text += f'{who}: {entry}\n'
        self.body.set_message_text(text)
        

    def send_msg(self):
        """
        Sends the message to the user, adds it to the active DSU file,
        calls set_message_box for the text to appear in the message_box widget.
        """
        try:
            msg = self.body.get_text_entry()
            self._current_profile.send_msg(msg, self.body.recipient)
            self._current_profile.save_profile(self._profile_filename)
            self.body.set_text_entry("")
            self.set_message_box()
        except AttributeError:
            error = "ERROR: Please create/open a file and click on a contact."
            print(error)
            self.footer.set_status(error)
        except TypeError:
            error = "ERROR: Please connect to WiFi, and check IP address and port."
            self.footer.set_status(error)
            
    def add_contact(self):
        """
        Creates the add_contact window under Settings, allows user to enter in a new contact, and saves recipient to file
        """
        self.contact = ""
        root_2 = tk.Tk()
        root_2.title("Add Contact")
        root_2.geometry('275x75')
        text_wid = tk.Text(root_2, height = 1, width = 10)
        text_wid.pack()

        def get_input():
            self.contact = text_wid.get('1.0', 'end').rstrip()
            self._current_profile._recipients.append(self.contact)
            self.body.insert_contact(self.contact)
            self._current_profile.save_profile(self._profile_filename)

        Ok_btn = tk.Button(root_2, height=1, width=10, text="OK", command=lambda: [get_input(), root_2.destroy()])
        Ok_btn.pack()

    def _draw(self):
        """
        Call only once, upon initialization to add widgets to root frame
        """
        # Build a menu and add it to the root frame.
        menu_bar = tk.Menu(self.root)
        self.root['menu'] = menu_bar
        menu_file = tk.Menu(menu_bar)
        settings_file = tk.Menu(menu_bar)
        menu_bar.add_cascade(menu=menu_file, label='File')
        settings_file.add_command(label = 'Add Contact', command = self.add_contact)
        
        menu_file.add_command(label='New', command=self.new_profile)
        menu_file.add_command(label='Open...', command=self.open_profile)
        menu_file.add_command(label='Close', command=self.close)
        menu_bar.add_cascade(menu = settings_file, label = 'Settings')

        # The Body and Footer classes must be initialized and packed into the root window.
        self.body = Body(self.root, self._current_profile)
        self.body.pack(fill=tk.BOTH, side=tk.TOP, expand=True)
        
        self.footer = Footer(self.root, save_callback=self.send_msg)
        self.footer.pack(fill=tk.BOTH, side=tk.BOTTOM)

    def check_task(self):
        """
        Retrieves the new messages form the DS server
        Places new timer event on the event queue by calling after (recursion)
        """
        try:
            if self._profile_filename is not None:
                self._current_profile.new_msg()
                self._current_profile.save_profile(self._profile_filename)
                self.set_message_box()
            self.root.after(5000, self.check_task)
        except TypeError:
            error = "ERROR: Please connect to WiFi, and check IP address and port."
            self.footer.set_status(error)

if __name__ == "__main__":
    # All Tkinter programs start with a root window
    main = tk.Tk()

    # 'title' assigns a text value to the Title Bar area of a window
    main.title("Chatter Hub | Real-Time Messaging")

    # This is just an arbitrary starting point
    main.geometry("600x400")

    # Adding this option removes some legacy behavior with menus that modern OSes don't support. 
    main.option_add('*tearOff', False)

    # Initialize the MainApp class, which is the starting point for the widgets used in the program
    main_instance = MainApp(main)

    # When update is called, we finalize the states of all widgets that have been configured within the root frame
    # update ensures that we get an accurate width and height reading based on the types of widgets we have used
    main.update()
    # minsize prevents the root window from resizing too small
    main.minsize(main.winfo_width(), main.winfo_height())
	#accepts delay time, and check_task function so new messages can pop up
    main.after(5000, main_instance.check_task)
    
    # Start up the event loop for the program
    main.mainloop()
