import tkinter as tk
from tkinter import messagebox , simpledialog , filedialog
from functools import partial
import gui_dc_fet
from PIL import Image, ImageTk
import extract_text

BG_COLOR = "#FECEB1"
FG_COLOR = "#e38e00"
BUTTON_COLOR = "#F0D2F0"
BUTTON_HOVER_COLOR = "#a020f0"
ENTRY_BG_COLOR = "#F0D2F0"
ENTRY_FG_COLOR = "#e38e00"
Cream = "#FECEB1"
orange = "#e38e00"
Purple ="#a020f0"
light_purple = "#F0D2F0"

def on_enter(e):
    """Handle button hover."""
    e.widget.config(bg=BUTTON_HOVER_COLOR)

def on_leave(e):
    """Handle button leave."""
    e.widget.config(bg=BUTTON_COLOR)
    
def get_float_inputs(prompts):
    """
    Helper to show a form dialog for multiple float inputs.

    Args:
        prompts (list): A list of prompt strings for the input fields.

    Returns:
        dict: A dictionary with prompt strings as keys and their corresponding float values as values.

    Raises:
        ValueError: If the user cancels or provides invalid inputs.
    """
    # Create a modal form window
    form_window = tk.Toplevel()
    form_window.title("Input of Circuit")
    form_window.geometry("600x700")
    form_window.grab_set()  # Make the window modal
    form_window.configure(bg=BG_COLOR)

    inputs = {}  # Store the input fields and their associated prompts
    entries = {}  # Store the Entry widgets for validation

    def submit():
        try:
            # Validate and collect inputs
            for prompt, entry in entries.items():
                value = entry.get().strip()
                if value == "":
                    raise ValueError(f"Field '{prompt}' cannot be empty.")
                inputs[prompt] = float(value)
            form_window.destroy()  # Close the form on success
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def cancel():
        # Cancel input
        inputs.clear()  # Ensure no values are returned
        form_window.destroy()

    # Create labels and entry fields for each prompt
    for i, prompt in enumerate(prompts):
        tk.Label(
            form_window,
            text=prompt,
            bg=BG_COLOR,
            fg=FG_COLOR,
            font=("Arial", 12),
            anchor="w",
        ).grid(row=i, column=0, padx=10, pady=5, sticky="w")
        entry = tk.Entry(
            form_window,
            font=("Arial", 12),
            width=20,
            bg=ENTRY_BG_COLOR,
            fg=ENTRY_FG_COLOR,
            relief="flat"
        )
        entry.grid(row=i, column=1, padx=10, pady=5)
        entries[prompt] = entry

    # Submit and Cancel buttons
    button_frame = tk.Frame(form_window)
    button_frame.grid(row=len(prompts)+1 , column=0, columnspan=2, pady=10)

    tk.Button(
        button_frame, text="Submit", command=submit, bg=light_purple, fg=orange, width=10
    ).pack(side="left")

    tk.Button(
        button_frame, text="Cancel", command=cancel, bg=light_purple, fg=orange, width=10
    ).pack(side="right")

    # Wait for the form to close
    form_window.wait_window()

    # Raise an error if the user cancels
    if not inputs:
        raise ValueError("Input cancelled or invalid.")

    return inputs


def show_output(result, details):
    # Create a new window
    root_output = tk.Tk()
    root_output.title("FET Analysis")
    root_output.configure(bg=BG_COLOR)


    # Display result label
    result_label = tk.Label(root_output, text=result, font=("Arial", 14, "bold"), bg=BG_COLOR, fg=Purple)
    result_label.pack(pady=20)

    # Display details label
    details_label = tk.Label(root_output, text=details, font=("Arial", 12), bg=BG_COLOR, fg=orange)
    details_label.pack(pady=10)

    # Start the main loop for the output window
    root_output.mainloop()

    
def select_state():
    def handle_selection(state):
        if state == 0:
            image_path = filedialog.askopenfilename(title="Select Image File")
            if not image_path:
                messagebox.showerror("Error", "No image selected!")
                return
            
            img = Image.open(image_path)
            img_display = ImageTk.PhotoImage(img)

            img_window = tk.Toplevel()
            img_window.title("Circuit Image")
            img_label = tk.Label(img_window, image=img_display)
            img_label.image = img_display 
            img_label.pack()

            circuit_type_input = get_float_inputs(["Enter Circuit Type 1-6 (the order is like priviose page)"])
            circuit_type = int(next(iter(circuit_type_input.values()), None))

            if circuit_type not in range(1, 7):
                circuit_type = None

            if not circuit_type or circuit_type not in range(1, 7):
                messagebox.showerror("Error", "Invalid Circuit Type!")
                return

            circuit_extractors = [extract_text.simple_circuit, extract_text.circuit, extract_text.complex_circuit]
            extract_func = circuit_extractors[min(circuit_type-1, 2)]
            circuit_values = extract_func(image_path)

            if circuit_values[0] is None:
                messagebox.showerror("Error", "Failed to extract circuit values.")
                return
            
            param_prompts = {
                1: ["Enter IDSS (Gate-Source Leakage Current):", "Enter VPO (Pinch-off Voltage):"],
                2: ["Enter K (transconductance parameter):", "Enter VT (voltage transformer):"],
                3: ["Enter IDSS (Gate-Source Leakage Current):", "Enter VPO (Pinch-off Voltage):"],
                4: ["Enter K (transconductance parameter):", "Enter VT (voltage transformer):"],
                5: ["Enter IDSS (Gate-Source Leakage Current):", "Enter VPO (Pinch-off Voltage):"],
                6: ["Enter K (transconductance parameter):", "Enter VT (voltage transformer):"]
            }
            
            inputs = get_float_inputs(param_prompts[circuit_type])
            
            
            if circuit_type == 1:
                result, details = gui_dc_fet.state_1_n_channel(
                circuit_values[0],  # VDD
                circuit_values[1],  # VGG
                circuit_values[2],  # RD
                inputs["Enter IDSS (Gate-Source Leakage Current):"],  
                inputs["Enter VPO (Pinch-off Voltage):"]
                )
            elif circuit_type == 2:
                result, details = gui_dc_fet.state_2_n_channel(
                circuit_values[0],  # VDD
                circuit_values[1],  # VGG
                circuit_values[2],  # RD
                inputs["Enter K (transconductance parameter):"],  
                inputs["Enter VT (voltage transformer):"]
                )
            elif circuit_type == 3:
                result, details = gui_dc_fet.state_3_n_channel(
                circuit_values[0],  # VDD
                circuit_values[1],  # RD
                circuit_values[2],  # RSS
                inputs["Enter IDSS (Gate-Source Leakage Current):"],  
                inputs["Enter VPO (Pinch-off Voltage):"]
                )
            elif circuit_type == 4:
                result, details = gui_dc_fet.state_4_n_channel(
                circuit_values[0],  # VDD
                circuit_values[1],  # RD
                circuit_values[2],  # RSS
                inputs["Enter K (transconductance parameter):"],  
                inputs["Enter VT (voltage transformer):"]
            )
            elif circuit_type == 5:
                result, details = gui_dc_fet.state_5_n_channel(
                circuit_values[0],  # VDD
                circuit_values[1],  # RD
                circuit_values[2],  # RG1
                circuit_values[3],  # RG2
                circuit_values[4],  # RSS
                inputs["Enter IDSS (Gate-Source Leakage Current):"],  
                inputs["Enter VPO (Pinch-off Voltage):"]
                )
            elif circuit_type == 6:
                result, details = gui_dc_fet.state_6_n_channel(
                circuit_values[0],  # VDD
                circuit_values[1],  # RD
                circuit_values[2],  # RG1
                circuit_values[3],  # RG2
                circuit_values[4],  # RSS
                inputs["Enter K (transconductance parameter):"],  
                inputs["Enter VT (voltage transformer):"]
                )
            else:
                messagebox.showerror("Error", "Invalid Circuit Type!")
                return
            show_output(result, details)
        else:
            if state == 1:
                prompts = [
                "Enter VGG (Gate Voltage) : ",
                "Enter VDD (Supply Voltage) : ",
                "Enter RD (Drain Resistance) : ",
                "Enter IDSS (Gate-Source Leakage Current) : ",
                "Enter VPO (Pinch-off Voltage) : "
                ]
                inputs = get_float_inputs(prompts)
                VGG = inputs["Enter VGG (Gate Voltage) : "]
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD (Drain Resistance) : "]
                IDSS = inputs["Enter IDSS (Gate-Source Leakage Current) : "]
                VPO = inputs["Enter VPO (Pinch-off Voltage) : "]
                result, details = gui_dc_fet.state_1_n_channel(VDD, VGG, RD, IDSS, VPO)
                show_output(result, details)
                
            elif state == 2:
                prompts = ["Enter VGG (Gate Voltage) : ",
                "Enter VDD (Supply Voltage) : ",
                "Enter RD (Drain Resistance) : ",
                "Enter K (transconductance parameter) : " ,
                "Enter VT (voltage transformer) : "
                ]
                inputs = get_float_inputs(prompts)
                VGG = inputs["Enter VGG (Gate Voltage) : "]
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD (Drain Resistance) : "]
                K = inputs["Enter K (transconductance parameter) : "]
                VT = inputs["Enter VT (voltage transformer) : "]
                result, details = gui_dc_fet.state_2_n_channel(VDD, VGG, RD, K, VT)
                show_output(result, details)

            elif state == 3:
                prompts = ["Enter RSS (Source-Source Resistance): ",
                "Enter VDD (Supply Voltage) : ",
                "Enter RD (Drain Resistance) : ",
                "Enter IDSS (Gate-Source Leakage Current) : ",
                "Enter VPO (Pinch-off Voltage) : "
                ]
                inputs = get_float_inputs(prompts)
                RSS = inputs["Enter RSS (Source-Source Resistance): "]
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD (Drain Resistance) : "]
                IDSS = inputs["Enter IDSS (Gate-Source Leakage Current) : "]
                VPO = inputs["Enter VPO (Pinch-off Voltage) : "]
                result, details = gui_dc_fet.state_3_n_channel(VDD, RD, RSS, IDSS, VPO)
                show_output(result, details)
                
            elif state == 4:
                prompts = ["Enter RSS (Source-Source Resistance): ",
                "Enter VDD (Supply Voltage) : ",
                "Enter RD (Drain Resistance) : ",
                "Enter K (transconductance parameter) : ",
                "Enter VT (voltage transformer) : "
                ]
                inputs = get_float_inputs(prompts)
                RSS = inputs["Enter RSS (Source-Source Resistance): "]
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD (Drain Resistance) : "]
                K = inputs["Enter K (transconductance parameter) : "]
                VT = inputs["Enter VT (voltage transformer) : "]
                result, details = gui_dc_fet.state_4_n_channel(VDD, RD , RSS, K, VT)
                show_output(result, details)
                
            elif state == 5:
                prompts = [
                    "Enter RSS (Source-Source Resistance) : ",
                    "Enter VDD (Supply Voltage) : ",
                    "Enter RD (Drain Resistance) : ",
                    "Enter RG1 (Gate Resistance) : ",
                    "Enter RG2 (Gate Resistance) : ",
                    "Enter IDSS (Gate-Source Leakage Current) : ",
                    "Enter VPO (Pinch-off Voltage) : "
                ]
                inputs = get_float_inputs(prompts)
                RSS = inputs["Enter RSS (Source-Source Resistance) : "]
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD (Drain Resistance) : "]
                RG1 = inputs["Enter RG1 (Gate Resistance) : "]
                RG2 = inputs["Enter RG2 (Gate Resistance) : "]
                IDSS = inputs["Enter IDSS (Gate-Source Leakage Current) : "]
                VPO = inputs["Enter VPO (Pinch-off Voltage) : "]
                result, details = gui_dc_fet.state_5_n_channel(VDD, RD, RG1, RG2, RSS, IDSS, VPO)
                show_output(result, details)

            elif state == 6:
                prompts = [
                    "Enter VDD (Supply Voltage) : ",
                    "Enter RD (Drain Resistance) : ",
                    "Enter RSS (Source-Source Resistance) : ",
                    "Enter RG1 (Gate Resistance) : ",
                    "Enter RG2 (Gate Resistance) : ",
                    "Enter K (transconductance parameter) : ",
                    "Enter VT (voltage transformer) : "
                ]
                inputs = get_float_inputs(prompts)
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD (Drain Resistance) : "]
                RSS = inputs["Enter RSS (Source-Source Resistance) : "]
                RG1 = inputs["Enter RG1 (Gate Resistance) : "]
                RG2 = inputs["Enter RG2 (Gate Resistance) : "]
                K = inputs["Enter K (transconductance parameter) : "]
                VT = inputs["Enter VT (voltage transformer) : "]
                result, details = gui_dc_fet.state_6_n_channel(VDD, RD, RG1, RG2, RSS, K, VT)
                show_output(result, details)

            elif state == 7:
                prompts = [
                    "Enter VDD (Supply Voltage) : ",
                    "Enter RD (Drain Resistance) : ",
                    "Enter RG (Gate Resistance) : ",
                    "Enter K (transconductance parameter) : ",
                    "Enter VT (voltage transformer) : "
                ]
                inputs = get_float_inputs(prompts)
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD (Drain Resistance) : "]
                RG = inputs["Enter RG (Gate Resistance) : "]
                K = inputs["Enter K (transconductance parameter) : "]
                VT = inputs["Enter VT (voltage transformer) : "]
                result, details = gui_dc_fet.state_7_n_channel(VDD, RD, RG, K, VT)
                show_output(result, details)

            elif state == 8:
                prompts = [
                    "Enter VDD (Supply Voltage) : ",
                    "Enter RD(Drain Resistance) : ",
                    "Enter RG (Gate Resistance) : ",
                    "Enter IDSS (Gate-Source Leakage Current) : ",
                    "Enter VPO (Pinch-off Voltage) : "
                ]
                inputs = get_float_inputs(prompts)
                VDD = inputs["Enter VDD (Supply Voltage) : "]
                RD = inputs["Enter RD(Drain Resistance) : "]
                RG = inputs["Enter RG (Gate Resistance) : "]
                IDSS = inputs["Enter IDSS (Gate-Source Leakage Current) : "]
                VPO = inputs["Enter VPO (Pinch-off Voltage) : "]
                result, details = gui_dc_fet.state_8_n_channel(VDD, RD, RG, IDSS, VPO)
                show_output(result, details)
                
            else:
                messagebox.showerror("Error", "Invalid state selection.")
                messagebox.showinfo("Selection", f"You selected: State {state}.")
            root.destroy()

    # Set up the main window
    root = tk.Tk()
    root.title("FET Analysis")
    root.configure(bg=BG_COLOR)
    root.geometry("800x650")


    tk.Label(root, text="Please select one of the following states:", font=("Arial bold", 14) ,bg= BG_COLOR ,fg = Purple).pack(pady=10)

    tk.Button(
    root,
    text=" Upload Picture",
    command=lambda: handle_selection(0),
    bg=BUTTON_COLOR,
    fg=FG_COLOR,
    font=("Arial", 12),
    relief="flat",
    width=40,
    height=2
    ).pack(pady=10)
    state_texts = {
        1: "VGG in JFET and Depletion MOSFET",
        2: "VGG in Enhancement MOSFET",
        3: "RSS in JFET and Depletion MOSFET",
        4: "RSS in Enhancement MOSFET",
        5: "RG1, RG2 in JFET and Depletion MOSFET",
        6: "RG1, RG2 in Enhancement MOSFET",
        7: "Biasing Circuit for JFET and Depletion MOSFET ",
        8: "Biasing Circuit for Enhancement MOSFET"
    }
    # Create buttons for each state (1 to 8)
    for i in range(1, 9):  # States 1 to 8
        tk.Button(
            root,
            text=f"{i}: {state_texts[i]}",
            command=lambda state=i: handle_selection(state),
            bg=BUTTON_COLOR,
            fg=FG_COLOR,
            font=("Arial", 12),
            relief="flat",
            width=40,
            height=2
        ).pack(pady=5)

    root.mainloop()