import sys
import tkinter as tk
from tkinter import ttk

from Service.TextInjectorService import TextInjectorService

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.utils import Input

from Agents.agent import ValidationAgent, ProductOwnerAgent

state = {"token": ""}


# Function to add label and text area
def add_input_field(parent, label_text, row):
    label = ttk.Label(parent, text=label_text + " :")
    label.grid(row=row, column=0, sticky="nw", padx=10, pady=(10, 0))

    text_box = tk.Text(parent, height=4, width=40)
    text_box.grid(row=row + 1, column=0, padx=10, pady=(0, 10))
    return text_box


# Function to handle "Enter" button click
def get_info(idee_widget, token_widget, validation_agent, product_owner_agent, ai_widget):
    idee = idee_widget.get("1.0", tk.END).strip()
    state["token"] = token_widget.get("1.0", tk.END).strip()
    print("Idée de projet:", idee)
    print("Access token github:", state["token"])

    # Reformulate the input
    reformulated_input = validation_agent.reformulate_input(idee)


# Function to handle "Validate" button click
def validate_response(ai_widget, validation_agent, product_owner_agent):
    reformulated_input = ai_widget.get("1.0", tk.END).strip()
    if validation_agent.create_github_repo(state["token"]):
        TextInjectorService.write("Repository github crée")

    product_owner_agent.split_task(reformulated_input)
    product_owner_agent.create_issues(validation_agent.repo_name, state["token"])


def main():
    # Main window
    root = tk.Tk()
    root.title("AI Project Assistant")
    root.geometry("1000x850")
    root.resizable(True, True)

    # === Left Frame
    left_frame = ttk.Frame(root)
    left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="n")

    # === Right Frame
    right_frame = ttk.Frame(root)
    right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="n")

    ai_label = ttk.Label(right_frame, text="Réponse de l'IA :")
    ai_label.pack(anchor="w")

    ai_text = tk.Text(right_frame, height=35, width=80)
    ai_text.pack(pady=(0, 10))

    TextInjectorService.init(ai_text)
    TextInjectorService.write("✅ Text area initialized successfully.")

    # Create instances of the agents
    validation_agent = ValidationAgent()
    product_owner_agent = ProductOwnerAgent()

    validate_button = ttk.Button(
        right_frame,
        text="Validate",
        command=lambda: validate_response(ai_text, validation_agent, product_owner_agent)
    )
    validate_button.pack()

    reformulate_button = ttk.Button(
        right_frame,
        text="Reformulate",
        command=lambda: validation_agent.reformulate_input(idee_text.get("1.0", tk.END).strip())
    )

    reformulate_button.pack()

    idee_text = add_input_field(left_frame, "Idée de projet", 0)
    token_text = add_input_field(left_frame, "Access token github", 2)

    enter_button = ttk.Button(
        left_frame,
        text="Enter",
        command=lambda: get_info(idee_text, token_text, validation_agent, product_owner_agent, ai_text)
    )

    enter_button.grid(row=4, column=0, pady=10)

    # Run the app
    root.mainloop()


if __name__ == "__main__":
    main()
