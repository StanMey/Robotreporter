class Article:
    """A Article class that holds all paragraphs and the chosen divider.
    """
    def __init__(self, pars: list):
        """The init function.

        Args:
            pars (list): A list with all the paragraphs to be in the article
        """
        self.paragraphs = pars  # saves the paragraphs
        self.par_divider = "<#new_par_here#>"  # the divider of the paragraphs
        self.observs_id = []  # stores the id's of the observations
        self.sit_relev = []  # stores the situational relevances of the observations

    def build(self, verbose: bool = False):
        """Goes over every paragraph and builds the article with the dividers between paragraphs.

        Args:
            verbose (bool, optional): Prints information about every added observation. Defaults to False.
        """
        self.content = ""
        for par in self.paragraphs:
            for observ in par.observations:

                # save the meta_data
                self.observs_id.append(observ.observ_id)
                self.sit_relev.append(observ.relevance2)

                # append the sentence to the article
                self.content += f"{observ.observation_new} "
                if verbose:
                    print(observ.year, observ.week_number, observ.day_number, observ.pattern, observ.observation_new)

            # end of paragraph (add a paragraph divider)
            self.content += self.par_divider
