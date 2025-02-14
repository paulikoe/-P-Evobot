import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
from subprocess import Popen, PIPE
import time
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
from time import sleep
from taking_photos import camera, camera_photo, camera_prepare
from run_yolov5 import run_yolov5_detection
from QReader import process_file
from coordinates_qr import coordinates
from coordinates_qr import get_QR
from choose import choose_assignment
from pipette_work import Program_1
from threading import Event


class Console(tk.Frame):
    """Simple console that can execute bash commands"""

    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        self.configure(bg="#2E2E2E")

        self.text_options = {
            "state": "disabled",
            "bg": "black",
            "fg": "gold", #nebo #3498DB
            "insertbackground": "gold",
            "selectbackground": "dodgerblue"
        }

        self.text = ScrolledText(self, **self.text_options,relief = "flat")
        self.text.pack(expand=True, fill="both")

        
        ''' Camera '''
        self.cap = None  # Initializing the cap variable
        self.camera_ready = threading.Event()  # Creating an event for synchronization
        # Starting a camera thread during GUI initialization
        threading.Thread(target=self.camera_thread).start()

        
        self.text.bind("<Return>", self.send_input)
        self.text.bind("<Key>", self.block_typing)  # Block typing except when necessary

        ''' Buttons '''
        # Button to start the script
        self.executer = tk.Button(self, text="Start Script", command=self.start_thread,
                                  bg='dodgerblue', fg='white', relief = "flat",
                                   font=('Helvetica', 10, 'bold') )  
        self.executer.pack(side="left", padx=5, pady=2)

        self.executer = tk.Button(self, text="Fast version", command=self.start_thread_fast,
                                  bg='dodgerblue', fg='white', relief = "flat",
                                 font=('Helvetica', 10, 'bold'))
        self.executer.pack(side="left", padx=5, pady=2)

        # Button to clear the console output
        self.clearer = tk.Button(self, text="Clear", command=self.clear,
                                 bg='dodgerblue', fg='white', relief = "flat",
                                 font=('Helvetica', 10, 'bold'))
        self.clearer.pack(side="left", padx=5, pady=2)

        # Button to stop the running script
        self.stopper = tk.Button(self, text="Stop", command=self.stop,
                                 bg='dodgerblue', fg='white', relief = "flat",
                                 font=('Helvetica', 10, 'bold'))
        self.stopper.pack(side="left", padx=5, pady=2)

        ''' Predefined commands '''
        self.command = ""  # Predefined command (script path)
        self.popen = None  # Will hold a reference to a Popen object
        self.running = False  # True if the process is running

        self.allow_typing = False  # Flag to allow typing when input is needed
        self.current_beaker = 0
        self.required_beakers = []
        self.indices = {}
        self.assignment = None

         # Initialize volume attributes
        self.volume1 = None
        self.volume2 = None

    
    def block_typing(self, event):
        """Prevent typing unless allow_typing is True"""
        if not self.allow_typing:
            return "break"  # Block typing when not allowed
    
    def stop(self):
        """It sends the robot to the home position"""
        program1 = Program_1()
        program1.home()
    
    def clear_text(self):
        """Clears the Text widget"""
        self.text.config(state="normal")
        self.text.delete(1.0, "end-1c")
        self.text.config(state="disabled")

    def clear(self, event=None):
        """Just clears the Text widget."""
        self.clear_text()
    
    def show(self, message, bold = False):
        # Always insert a new message on a new line
        self.text.config(state="normal")  # Enable text editing
        current_text = self.text.get("end-3c", "end-1c")  # Get the last character

        # If the last character is not a newline, insert one before the new message
        if current_text != "\n":
            self.text.insert(tk.END, "\n")

        if bold:
            self.text.tag_configure("bold", font=("Calibri", 11,"bold"))  # Nastavit tučný text
            self.text.insert(tk.END, message, "bold")  # Přidat tučný text
        else:
            self.text.insert(tk.END, message)  # Přidat normální text
        
        self.text.config(state="disabled")  # Disable editing after insertion
        self.text.see(tk.END)  # Scroll to the end of the text area if needed

        
    
    ''' START '''
    

    def start_thread(self):
        """Clicking on the start button starts the run_control 
        system function in another thread - so the script will 
        run in a different thread than the gui"""

        threading.Thread(target=self.run_control_system).start()

    def start_thread_fast(self):
        """Clicking on the start button starts the run_control 
        system (fast version) function in another thread - so the script will 
        run in a different thread than the gui
        This version skips detection and obtaining coordinates. 
        It is used for quick access if the user has already 
        performed detection (Start button) once."""

        threading.Thread(target=self.run_control_system_fast).start()

    def camera_thread(self):
        """Starting the camera on a separate thread"""
        camera_prepare(self)
        

    def run_control_system_fast(self):
        self.show("Loading valid QR indices...")
        self.QR_index = get_QR()  # Load valid QR indices
        self.seen_indices = set()  # To track used indices
        self.show(f"QR Index: {self.QR_index}")


        self.show("Choosing assignment...")
        self.prompt_for_assignment()  # Prompt for assignment

    def run_control_system(self):
        """Runs the control system and updates the GUI
        The functions of the control system are gradually activated"""
        
        self.show("Starting camera...")
        #camera(self)  # Camera is on
        self.camera_ready.wait() # Waiting until the camera is ready
        camera_photo(self)
        
        self.show("Running YOLOv5 detection...")
        run_yolov5_detection()  # Run the detection
        self.show("Detection complete!")
        
        self.show("Processing file...")
        process_file()  # QR code reader
        self.show("File processed!")

        self.show("Converting coordinates...")
        coordinates()  # Converting coordinates
        self.show("Coordinates converted!")

        self.show("Loading valid QR indices...")
        self.QR_index = get_QR()  # Load valid QR indices
        self.seen_indices = set()  # To track used indices
        self.show(f"QR Index: {self.QR_index}")
        
        self.show("Choosing assignment...")
        self.prompt_for_assignment()  # Prompt for assignment
        
    def prompt_for_assignment(self, event=None):
        self.show("You have XY options:\n1. Mixing two liquids.\n2. Pipetting from one beaker to the target beaker.\nTo select, enter a digit: ")
        self.text.config(state="normal")
        self.allow_typing = True  # Allow user to write
        self.text.focus()  # Focus on text area for user input
    
    def send_input(self, event=None):
        """Handles user input when Enter is pressed"""
        if self.allow_typing:
            user_input = self.text.get("end-3c", "end-1c").strip()  # User input
            self.text.config(state="disabled")
            self.allow_typing = False
            

            if self.assignment is None:  # Assignment selection - možná špatně napsané, byla zvolena 1, ale v GUI je zatim nastaveno na None
                self.process_assignment_input(user_input)  # Call separate function for assignment input
            else:  # Handling beaker input
                self.handle_beaker_input(user_input) # Beakers input
    
        return "break"
    
    def process_assignment_input(self, assignment_input):
        """Processes the user's assignment selection"""
        if assignment_input:  # Verification that the input is not empty
                self.show(f"You selected: {assignment_input}")
                self.allow_typing = False  # Prohibiting further writing
                self.text.config(state="disabled")  # Lock the text field

                if assignment_input == "1":
                    self.required_beakers = ["leftovers", "water", "goal beaker", "beaker1", "beaker2"]
                elif assignment_input == "2":
                    self.required_beakers = ["leftovers", "water", "beaker1", "goal beaker"]
                else:
                    self.show("Invalid assignment. Please enter 1 or 2.")
                    self.prompt_for_assignment() # if no valid request is entered, the program will ask again
                    return

                # Assignment is set, now prompt for beaker indices
                self.assignment = assignment_input
                self.current_beaker = 0  # Start at the first beaker
                self.ask_for_next_beaker()  # Prompt the user for the first beaker index
        else:
            self.show("Invalid input. Please enter a valid number.")  # Handle invalid input


    def ask_for_next_beaker(self):
        """Prompts the user for the next beaker index"""
        beaker = self.required_beakers[self.current_beaker] # # Get the current beaker in order from the list
        # clicking on Enter (self.text.bind("<Return>", self.send_input)) - code goes back to input
        # and the function ( handle_beaker_input) will start
        self.show(f"Write index of beaker for {beaker}: ") 
        self.text.config(state="normal")
        self.allow_typing = True
        self.text.focus()


    def handle_beaker_input(self, indices_from_gui):
        """Handles input for beaker indices with validation"""
        # Check if there are more beakers to process
        if self.current_beaker < len(self.required_beakers):
            if indices_from_gui.isdigit(): # Ensure the input is a valid number
                beaker = self.required_beakers[self.current_beaker] # Get the current beaker
                index = int(indices_from_gui) # Convert the input to an integer

                # Check if the index is in the valid list of QR indices
                if index not in self.QR_index:
                    self.show(f"Error: Index {index} for {beaker} is not valid.")
                    self.ask_for_next_beaker() # Re-prompt for the same beaker

                # Check if the index has already been used for another beaker
                elif index in self.seen_indices:
                    self.show(f"Error: Index {index} for {beaker} has already been used.")
                    self.ask_for_next_beaker() # Re-prompt for the same beaker
                else:
                    # If valid and not duplicated, save the index for the current beaker
                    self.indices[beaker] = index
                    self.seen_indices.add(index)  # Mark index as used
                    self.current_beaker += 1 # Move to the next beaker

                    # Check if there are more beakers to process
                    if self.current_beaker < len(self.required_beakers):
                        self.ask_for_next_beaker() # Prompt for the next beaker's index
                    else:
                        # If all beakers are processed, display a message and move to the next phase
                        self.show("All indices are set.")
                        self.ask_for_volumes()  # Proceed to the volume input phase
            else:
                # If input is not a valid number, show an error and re-prompt for input
                self.show("Invalid input. Please enter a valid number.")
                self.ask_for_next_beaker()
        else:
            # If there are no more beakers to process, inform the user
            self.show("No more beakers to process.")


    def ask_for_volumes(self):
            """Prompt the user for volumes based on assignment."""
            if self.assignment == "1":
                self.show("Select volume for beaker 1 (ml) (In this form: 0.35): ") 
                self.text.config(state="normal")
                self.allow_typing = True
                self.text.focus()
                self.text.bind("<Return>", self.get_volume_assignment1) #for assignment 1
            elif self.assignment == "2":
                self.show("Select volume for beaker 1 (ml) (In this form: 0.35): ")
                self.text.config(state="normal")
                self.allow_typing = True
                self.text.focus()
                self.text.bind("<Return>", self.get_volume_assignment2) #for assignment 2
  
           
    def get_volume_assignment1(self, event=None):
        """Get volume for beaker 1."""
        max_volume = 9.00
        try:
            # First, get the user input and convert it to an integer
            self.volume1 = float(self.text.get("end-5c", "end-1c").strip())
            
            # Now, check if the entered volume exceeds the maximum allowed volume
            if self.volume1 > max_volume:
                self.show(f"Volume exceeds the maximum limit of {max_volume} ml. Please enter a smaller value.")
                self.ask_for_volumes()
                return  # Exit the function if the volume is too high
            
            # Proceed if the volume is within the allowed limit
            #self.show(f"Volume for beaker 1 set to {self.volume1} ml.")
            self.show("Select volume for beaker 2 (ml) (In this form: 0.35): ")
            self.text.config(state="normal")  # Make the input field editable
            self.allow_typing = True
            self.text.focus()
            self.text.bind("<Return>", self.get_volume2_assignment1) # Bind the next function for volume 2

        except ValueError:
            # Handle the error if the input is invalid
            self.show("Invalid input. Please enter a valid number.")  # Show error in GUI
            self.ask_for_volumes()
       

    def get_volume2_assignment1(self, event=None):
        """Get volume for beaker 2 for assignment 1."""
        max_volume = 9.00
        try:
            self.volume2 = float(self.text.get("end-6c", "end-1c").strip())
            self.text.config(state="normal")
            self.allow_typing = True
            self.text.focus()
            # Now, check if the entered volume exceeds the maximum allowed volume
            if self.volume2 > max_volume:
                self.show(f"Volume exceeds the maximum limit of {max_volume} ml. Please enter a smaller value.")
                self.volume2_error()
                return  # Exit the function if the volume is too high
            else:
                self.show("connected to (P)EvoBot")
                self.text.update_idletasks()
                self.show("The robot has started")
                self.text.update_idletasks()

            #self.show(f"Volume for beaker 2 set to {self.volume2} ml.")
            # Focus the cursor immediately after setting the text
            try:
                choose_assignment(self.assignment, self.indices, self.volume1, self.volume2)
            except ValueError as e:
                self.show(f"Error: {str(e)}")  # Zobrazení chyby v GUI
             
        except ValueError:
            # Handle the error if the input is invalid
            self.show("Invalid input. Please enter a valid number.")  # Show error in GUI
            self.volume2_error()

    def volume2_error(self, event= None):
        self.show("Select volume for beaker 2 (ml) (In this form: 0.35): ")
        self.text.config(state="normal")
        self.allow_typing = True
        self.text.bind("<Return>", self.get_volume2_assignment1)


    def get_volume_assignment2(self,event=None):
        """Get volume for beaker 1."""
        max_volume = 9.00
        try:
            self.volume1 = float(self.text.get("end-5c", "end-1c").strip())
            if self.volume1 > max_volume:
                self.show(f"Volume exceeds the maximum limit of {max_volume} ml. Please enter a smaller value.")
                self.ask_for_volumes()
                return  # Exit the function if the volume is too high
            #self.show(f"Volume for beaker 1 set to {self.volume1} ml.")
            else:
                self.show("connected to (P)EvoBot")
                self.text.update_idletasks()
                self.show("The robot has started")
                self.text.update_idletasks()
            try:
                choose_assignment(self.assignment, self.indices, self.volume1,self.volume2)
            except ValueError as e:
                self.show(f"Error: {str(e)}")  # Zobrazení chyby v GUI

        except ValueError:
            # Handle the error if the input is invalid
            self.show("Invalid input. Please enter a valid number.")  # Show error in GUI
            self.ask_for_volumes()



if __name__ == "__main__":
    root = tk.Tk()
    root.title("(P)EvoBot")
    console = Console(root)
    console.pack(expand=True, fill="both")
    root.mainloop()
