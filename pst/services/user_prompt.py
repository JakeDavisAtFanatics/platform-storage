from typing import List


class UserPromptService:
    def __init__(self, title: str, options: List[str], prompt: str = "Select an option (default 1): "):
        self.title = title
        self.options = options
        self.prompt = prompt

    def get_selection(self) -> str:
        print(f"\n{self.title}:")
        for i, option in enumerate(self.options, 1):
            print(f"{i}. {option}")

        while True:
            try:
                choice = input(self.prompt).strip()
                if choice == "":
                    return self.options[0]  # Return the first option as default
                choice = int(choice)
                if 1 <= choice <= len(self.options):
                    return self.options[choice - 1]
                else:
                    print("Invalid selection. Please try again.")
            except ValueError:
                print("Invalid input. Please enter a number.")
