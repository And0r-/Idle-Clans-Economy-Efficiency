class AsciiUI:
    def __init__(self):
        self.width = 40
        print("TEMP: ASCIIUI INIT")

    def _generate_menu(self, title: str, options: list, display_exit=False):
        print("TEMP: MENU")
        if len(options > 9):
            # currently uses str comp :+13
            raise NotImplementedError
        padding = (self.width - len(title)) // 2
        border = "=" * self.width

        print(border)
        print(" " * padding + title + " " * padding)
        print(border)
        for i, option in enumerate(options):
            print(f"{i+1}: {option}")
        print(f"0: {'Exit' if display_exit else 'back'}")
        print(border)
        usr = input("Please choose an option: ")
        while usr < "0" or usr > str(len(options)):
            usr = input("Please choose an option: ")
        return usr

    def menu(self):
        """
        options:\n
        1: Calculate Gold Efficiency\n
        2: Market Search\n
        3: Reload Data\n
        4: Settings\n
        """
        print("TEMP: MENU")
        self._generate_menu(
            "Idle Clans Menu",
            ["Calculate Gold Efficiency", "Market Search", "Reload Data", "Settings"],
            display_exit=True,
        )

    def menu(self):
        """
        Not Implemented
        """
        return None

    def reload_data(self):
        """
        options:\n
        1: Reload Items Data\n
        2: Reload Player Data\n
        3: Auto Reload Settings\n
        """
        self._generate_menu(
            "Reload Data",
            ["Reload Items Data", "Reload Player Data", "Auto Reload Settings"],
        )

    def calculate_gold_efficiency(self):
        """
        options:\n
        1: Global\n
        2: Player bound\n
        """
        self._generate_menu(
            "Calculate Gold Efficiency",
            ["Global", "Player bound"],
        )

    def settings(self):
        """
        options:\n
        1: Global\n
        2: Player bound\n
        """
        self._generate_menu(
            "Settings",
            ["Global", "Player bound"],
        )
