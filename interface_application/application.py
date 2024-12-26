import tkinter as tk
from tkinter import ttk, messagebox
import requests
from tokens import ADMIN_TOKEN
class FlightPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flight Planner API")

        self.create_widgets()

    def create_widgets(self):
        # Input for endpoint path
        tk.Label(self.root, text="API Endpoint Path").grid(row=0, column=0, padx=10, pady=5)
        self.endpoint_entry = tk.Entry(self.root, width=50)
        self.endpoint_entry.grid(row=0, column=1, padx=10, pady=5)

        # Input for JSON payload
        tk.Label(self.root, text="JSON Payload").grid(row=1, column=0, padx=10, pady=5)
        self.json_entry = tk.Text(self.root, height=10, width=50)
        self.json_entry.grid(row=1, column=1, padx=10, pady=5)

        # Dropdown for selecting request type
        tk.Label(self.root, text="Request Type").grid(row=2, column=0, padx=10, pady=5)
        self.request_type = ttk.Combobox(self.root, values=["GET", "POST", "PUT", "DELETE"])
        self.request_type.grid(row=2, column=1, padx=10, pady=5)
        self.request_type.current(0)  # Default to GET

        # Button to send request
        self.send_button = tk.Button(self.root, text="Send Request", command=self.send_request)
        self.send_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Output for API response
        tk.Label(self.root, text="API Response").grid(row=4, column=0, padx=10, pady=5)
        self.response_box = tk.Text(self.root, height=15, width=80, state=tk.DISABLED)
        self.response_box.grid(row=4, column=1, columnspan=2, padx=10, pady=5)

    def send_request(self):
        endpoint = self.endpoint_entry.get()
        admin_token = ADMIN_TOKEN  # Replace with your actual admin token
        headers = {"Authorization": f"Bearer {admin_token}"}

        try:
            json_data = self.json_entry.get("1.0", tk.END).strip()
            json_payload = None
            if json_data:
                json_payload = eval(json_data)  # Safely parse JSON

            url = f"http://localhost:5000{endpoint}"  # Adjust base URL as needed
            request_type = self.request_type.get()  # Get selected request type

            # Determine HTTP method based on selected type
            if request_type == "GET":
                response = requests.get(url, headers=headers, params=json_payload)
            elif request_type == "POST":
                response = requests.post(url, headers=headers, json=json_payload)
            elif request_type == "PUT":
                response = requests.put(url, headers=headers, json=json_payload)
            elif request_type == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError("Unsupported request type")

            # Process response
            if response.status_code == 204:  # No Content
                self.display_response({"message": "Successfully deleted."})
            else:
                self.display_response(response.json())
        except Exception as e:
            self.display_response({"error": str(e)})

    def display_response(self, response):
        self.response_box.configure(state=tk.NORMAL)
        self.response_box.delete("1.0", tk.END)
        self.response_box.insert(tk.END, str(response))
        self.response_box.configure(state=tk.DISABLED)

# Main application
if __name__ == "__main__":
    root = tk.Tk()
    app = FlightPlannerApp(root)
    root.mainloop()
