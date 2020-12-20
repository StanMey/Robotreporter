class DateMessage:
    def __init__(self):
        pass

    @staticmethod
    def day_to_string(day_number):
        """Gets the number of the current day (Between 0 and 6 inclusive) and returns the dutch translation.

        Args:
            day_number (int): The number of the weekday

        Returns:
            String: The dutch word for the current day
        """
        numb_to_weekday = {
            0: "maandag",
            1: "dinsdag",
            2: "woensdag",
            3: "donderdag",
            4: "vrijdag",
            5: "zaterdag",
            6: "zondag",
        }

        return numb_to_weekday.get(day_number)

    @staticmethod
    def month_to_string(month_number):
        """Gets the number of the month (Between 1 and 12 inclusive) and returns a string with the dutch version of that month.

        Args:
            month_number (int): The number of the month

        Returns:
            String: The dutch word for the current month
        """
        numb_to_month = {
            1: "januari",
            2: "februari",
            3: "maart",
            4: "april",
            5: "mei",
            6: "juni",
            7: "juli",
            8: "augustus",
            9: "september",
            10: "oktober",
            11: "november",
            12: "december"
        }

        return numb_to_month.get(month_number)

    @staticmethod
    def day_difference_to_string(x_diff: int, current_based: bool):
        """[summary]

        Args:
            x_diff (int): [description]
            current_based (bool): [description]

        Returns:
            [type]: [description]
        """
        if current_based:
            if x_diff == 0:
                sentence = "vandaag"
            elif x_diff == 1:
                sentence = "gisteren"
            elif x_diff == 2:
                sentence = "eergisteren"
            else:
                sentence = f"{x_diff} dagen geleden"
        else:
            if x_diff == 0:
                sentence = "dezelfde dag"
            elif x_diff == 1:
                sentence = "de dag daarvoor"
            else:
                sentence = f"{x_diff} dagen daarvoor"

        return sentence

    @staticmethod
    def explicit_day_difference_to_string(day_number: int):
        """[summary]

        Args:
            day_number (int): The number of the day of the week

        Returns:
            [type]: [description]
        """
        sentence = f"de {DateMessage.day_to_string(day_number)} ervoor"
        return sentence

    @staticmethod
    def week_difference_to_string(x_diff: int, current_based: bool):
        """[summary]

        Args:
            x_diff (int): [description]
            current_based (bool): [description]

        Returns:
            str: [description]
        """
        if current_based:
            if x_diff == 0:
                sentence = "deze week"
            elif x_diff == 1:
                sentence = "vorige week"
            else:
                sentence = f"{x_diff} weken geleden"
        else:
            if x_diff == 0:
                sentence = "dezelfde week"
            elif x_diff == 1:
                sentence = "de week daarvoor"
            else:
                sentence = f"{x_diff} weken daarvoor"

        return sentence

    @staticmethod
    def explicit_week_difference_to_string(day_number: int):
        """[summary]

        Args:
            day_number (int): [description]

        Returns:
            str: [description]
        """
        sentence = f"de week ervoor op {DateMessage.day_to_string(day_number)}"
        return sentence

    @staticmethod
    def month_difference_to_string(x_diff: int, current_based: bool):
        """[summary]

        Args:
            x_diff (int): [description]
            current_based (bool): [description]

        Returns:
            [type]: [description]
        """
        if current_based:
            if x_diff == 0:
                sentence = "deze maand"
            elif x_diff == 1:
                sentence = "vorige maand"
            else:
                sentence = f"{x_diff} maanden geleden"
        else:
            if x_diff == 0:
                sentence = "dezelfde maand"
            elif x_diff == 1:
                sentence = "de maand daarvoor"
            else:
                sentence = f"{x_diff} maanden daarvoor"

        return sentence
