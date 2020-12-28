class DateMessage:
    """A class which holds static methods that assist by translating date related sentences to dutch words.
    """

    @staticmethod
    def day_to_string(day_number):
        """Gets the number of the current day (Between 0 and 6 inclusive) and returns the dutch translation.

        Args:
            day_number (int): The number of the weekday

        Returns:
            String: The dutch word for the current day
        """
        assert 0 <= day_number <= 6, "day has to be between 0 and 6 inclusive (via np.weekday())"

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
        assert 1 <= month_number <= 12, "month has to be between 1 and 12 inclusive"

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
    def number_to_string(number):
        """Gets a number and returns a string with the dutch version of the number if it's between 1 and 20.

        Args:
            number (int): The number to translate

        Returns:
            str: The string representation of the number
        """

        numb_to_string = {
            1: "een",
            2: "twee",
            3: "drie",
            4: "vier",
            5: "vijf",
            6: "zes",
            7: "zeven",
            8: "acht",
            9: "negen",
            10: "tien",
            11: "elf",
            12: "twaald",
            13: "dertien",
            14: "veertien",
            15: "vijftien",
            16: "zestien",
            17: "zeventien",
            18: "achttien",
            19: "negentien",
            20: "twintig"
        }

        return numb_to_string.get(number) if numb_to_string.get(number) else str(number)

    @staticmethod
    def day_difference_to_string(x_diff: int, current_based: bool):
        """Returns the day difference to be used for referencing between observations.

        Args:
            x_diff (int): The day difference between the two observations
            current_based (bool): If the article is being written from the 'more recent' perspective

        Returns:
            str: Returns a day difference reference string
        """
        if current_based:
            if x_diff == 0:
                sentence = "vandaag"
            elif x_diff == 1:
                sentence = "gisteren"
            elif x_diff == 2:
                sentence = "eergisteren"
            else:
                sentence = f"{DateMessage.number_to_string(x_diff)} dagen geleden"
        else:
            if x_diff == 0:
                sentence = "dezelfde dag"
            elif x_diff == 1:
                sentence = "de dag daarvoor"
            else:
                sentence = f"{DateMessage.number_to_string(x_diff)} dagen daarvoor"

        return sentence

    @staticmethod
    def explicit_day_difference_to_string(day_number: int, current_based: bool):
        """Returns the reference sentence for the explicit day.

        Args:
            day_number (int): The number of the day of the week
            current_based (bool): If the article is being written from the 'more recent' perspective

        Returns:
            str: Returns an explicit day difference reference string
        """
        if current_based:
            sentence = f"de {DateMessage.day_to_string(day_number)} hiervoor"
        else:
            sentence = f"de {DateMessage.day_to_string(day_number)} ervoor"
        return sentence

    @staticmethod
    def week_difference_to_string(x_diff: int, current_based: bool):
        """Returns the week difference to be used for referencing between observations.

        Args:
            x_diff (int): The week difference between the two observations
            current_based (bool): If the article is being written from the 'more recent' perspective

        Returns:
            str: Returns a week difference reference string
        """
        if current_based:
            if x_diff == 0:
                sentence = "deze week"
            elif x_diff == 1:
                sentence = "vorige week"
            else:
                sentence = f"{DateMessage.number_to_string(x_diff)} weken geleden"
        else:
            if x_diff == 0:
                sentence = "dezelfde week"
            elif x_diff == 1:
                sentence = "de week daarvoor"
            else:
                sentence = f"{DateMessage.number_to_string(x_diff)} weken daarvoor"

        return sentence

    @staticmethod
    def explicit_week_difference_to_string(day_number: int, current_based: bool):
        """Returns the explicit week difference to be used for referencing between observations.

        Args:
            day_number (int): The day number to refer to (see function day_to_string())
            current_based (bool): If the article is being written from the 'more recent' perspective

        Returns:
            str: Returns an explicit week difference reference string
        """
        if current_based:
            sentence = f"de week hiervoor op {DateMessage.day_to_string(day_number)}"
        else:
            sentence = f"de week ervoor op {DateMessage.day_to_string(day_number)}"
        return sentence

    @staticmethod
    def month_difference_to_string(x_diff: int, current_based: bool):
        """Returns the month difference to be used for referencing between observations.

        Args:
            x_diff (int): The month difference between the two observations
            current_based (bool): If the article is being written from the 'more recent' perspective

        Returns:
            str: Returns a month difference reference string
        """
        if current_based:
            if x_diff == 0:
                sentence = "deze maand"
            elif x_diff == 1:
                sentence = "vorige maand"
            else:
                sentence = f"{DateMessage.number_to_string(x_diff)} maanden geleden"
        else:
            if x_diff == 0:
                sentence = "dezelfde maand"
            elif x_diff == 1:
                sentence = "de maand daarvoor"
            else:
                sentence = f"{DateMessage.number_to_string(x_diff)} maanden daarvoor"

        return sentence
