import spacy

# Load SpaCy model
nlp = spacy.load("en_core_web_sm")


class BubbleTeaBot:
    def __init__(self):
        self.state = "greeting"
        self.order = {
            "drink_type": None,
            "flavor": None,
            "size": None,
            "sugar": None,
            "ice": None,
            "milk": None,
        }
        self.orders = []  # List to keep track of multiple orders
        self.menu = {
            "Fruit Tea": ["Mango", "Strawberry", "Peach", "Passion", "Tropical", "Greenapple", "Lychee", "Cherry", "Watermelon"],
            "Milk Tea": ["Strawberry", "Banoffee", "Caramel", "Taro", "Mango", "Watermelon", "Classic Black", "Green Jasmine", "Roasted Oolong"],
            "Epic Tea": ["Oreo", "Nutella", "Biscoff", "Bueno White"]
        }
        self.responses = {
            "greeting": "Hello! Welcome to our bubble tea shop! What drink would you like to order?'|wave",
            "flavor_selection": "You chose {drink_type}. What flavor would you like?.|open_hand",
            "size_selection": "You chose {flavor} {drink_type}. What size would you like? Regular or Large?|open_hand",
            "sugar_selection": "You chose {flavor} {drink_type} with size {size}. What sugar level would you like?|thinking",
            "ice_selection": "You chose {flavor} {drink_type} with {sugar}. What ice level would you like?|thinking",
            "milk_selection": "What type of milk would you like?|open_hand",
            "confirmation": "You ordered a {size} {flavor} {drink_type} with {sugar}, {ice}{milk}. Is that correct? |nod",
            "anything_else": "Would you like to order anything else? |open_hand",
            "payment": "The total price for your order is {total_price:.2f}pound. Would you like to proceed to payment? |point",
            "total_price": "Your total is £{total_price:.2f}. Would you like to proceed to payment?|point",
            "unknown": "I'm sorry, I didn't understand that. Can you please repeat?|thinking"
        }
        self.size_prices = {
            "regular": 4.89,
            "large": 5.29
        }

    def calculate_total(self):
        """Calculate the total price of all orders."""
        return sum(self.size_prices[order["size"]] for order in self.orders)

    def parse_customer_input(self, user_input):
        """Parse the customer input to identify order details."""
        user_input = user_input.lower().strip()

        # Define keywords
        drink_keywords = {
            "fruit tea": ["fruit tea"],
            "milk tea": ["milk tea"],
            "epic tea": ["epic tea"]
        }
        flavor_keywords = [flavor.lower() for flavor in self.menu["Fruit Tea"] + self.menu["Milk Tea"] + self.menu["Epic Tea"]]
        size_keywords = ["regular", "large"]
        sugar_keywords = ["no sugar", "less sugar", "standard sugar", "more sugar", "extra sugar"]
        ice_keywords = ["no ice", "less ice", "standard ice", "more ice", "extra ice"]
        milk_keywords = ["creamer", "fresh milk", "oat milk", "soya milk"]

        # Initialize fields
        drink_type, flavor, size, sugar, ice, milk = None, None, None, None, None, None

        # Match drink type
        for key, values in drink_keywords.items():
            if any(option in user_input for option in values):
                drink_type = key
                break

        # Match other fields
        if any(option in user_input for option in flavor_keywords):
            flavor = next(option for option in flavor_keywords if option in user_input)
        if any(option in user_input for option in size_keywords):
            size = next(option for option in size_keywords if option in user_input)
        if any(option in user_input for option in sugar_keywords):
            sugar = next(option for option in sugar_keywords if option in user_input)
        if any(option in user_input for option in ice_keywords):
            ice = next(option for option in ice_keywords if option in user_input)
        if any(option in user_input for option in milk_keywords):
            milk = next(option for option in milk_keywords if option in user_input)

        return drink_type, flavor, size, sugar, ice, milk

    def get_response(self, user_input):
        """Generate a response based on the current state and user input."""
        user_input = user_input.lower().strip()

        # Handle greeting
        if self.state == "greeting":
            self.state = "ordering"
            return self.responses["greeting"]

        # Handle ordering process
        if self.state == "ordering":
            drink_type, flavor, size, sugar, ice, milk = self.parse_customer_input(user_input)

            # Update fields in the current order
            if drink_type and not self.order["drink_type"]:
                self.order["drink_type"] = drink_type
            if flavor and not self.order["flavor"]:
                self.order["flavor"] = flavor
            if size and not self.order["size"]:
                self.order["size"] = size
            if sugar and not self.order["sugar"]:
                self.order["sugar"] = sugar
            if ice and not self.order["ice"]:
                self.order["ice"] = ice
            if milk and not self.order["milk"]:
                self.order["milk"] = milk

            # Check for missing details
            if not self.order["flavor"]:
                if self.order["drink_type"]:
                    return self.responses["flavor_selection"].format(
                        drink_type=self.order["drink_type"],
                        flavors=", ".join(self.menu[self.order["drink_type"].title()])
                    )
            if not self.order["size"]:
                return self.responses["size_selection"].format(
                    drink_type=self.order["drink_type"],
                    flavor=self.order["flavor"]
                )
            if not self.order["sugar"]:
                return self.responses["sugar_selection"].format(
                    drink_type=self.order["drink_type"],
                    flavor=self.order["flavor"], size=self.order["size"]
                )
            if not self.order["ice"]:
                return self.responses["ice_selection"].format(
                    drink_type=self.order["drink_type"],
                    flavor=self.order["flavor"], sugar=self.order["sugar"]
                )
            if self.order["drink_type"] == "milk tea" and not self.order["milk"]:
                return self.responses["milk_selection"]

            # Move to confirmation if all order details are filled
            if (
                self.order["drink_type"]
                and self.order["flavor"]
                and self.order["size"]
                and self.order["sugar"]
                and self.order["ice"]
                and (self.order["drink_type"] != "milk tea" or self.order["milk"])
            ):
                self.state = "confirmation"
                milk_text = f" with {self.order['milk']}" if self.order["milk"] else ""
                return self.responses["confirmation"].format(
                    drink_type=self.order["drink_type"],
                    flavor=self.order["flavor"], size=self.order["size"],
                    sugar=self.order["sugar"], ice=self.order["ice"],
                    milk=milk_text
                )

        # Handle confirmation response
        if self.state == "confirmation":
            if user_input.startswith("y"):
                self.orders.append(self.order.copy())
                self.order = {key: None for key in self.order}  # Reset for next order
                self.state = "anything_else"
                return self.responses["anything_else"]
            elif user_input.startswith("n"):
                self.state = "ordering"
                return "Okay, let's start over! What drink would you like?"

        # Handle additional orders
        if self.state == "anything_else":
            if user_input.startswith("y"):
                self.state = "ordering"
                return "Great! What else would you like to order?"
            elif user_input.startswith("n"):
                total_price = self.calculate_total()
                self.state = "payment"
                return self.responses["payment"].format(total_price=total_price)

        # Handle payment
        if self.state == "payment":
            if user_input.startswith("y"):
                self.state = "completed"
                return "Thank you for your payment! Your order is complete. Enjoy your bubble tea! |finished"
            elif user_input.startswith("n"):
                self.state = "completed"
                return "You can pay later. Your order has been noted. |finished"

        # Handle completed state
        if self.state == "completed":
            return "Thank you for visiting our bubble tea shop. Have a great day! |finished"

        # Default fallback
        return self.responses["unknown"]


# Main interaction loop
def chat():
    bot = BubbleTeaBot()
    print("Bubble Tea Bot: Hi! Welcome to our bubble tea shop.")
    while True:
        user_input = input("You: ")
        response = bot.get_response(user_input)
        print(f"Bubble Tea Bot: {response}")
        if bot.state == "completed":
            break


if __name__ == "__main__":
    chat()
