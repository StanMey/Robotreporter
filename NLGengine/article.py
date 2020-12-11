class Article:
    """[summary]
    """
    def __init__(self, pars: list):
        """[summary]

        Args:
            pars (list): [description]
        """
        self.paragraphs = pars  # saves the paragraphs
        self.par_divider = "<#new_par>"  # the divider of the paragraphs
        self.observs_id = []  # stores the id's of the observations
        self.sit_relev = []  # stores the situational relevances of the observations

    def build(self):
        """[summary]
        """
        self.content = ""
        for par in self.paragraphs:
            for observ in par.observations:

                # save the meta_data
                self.observs_id.append(observ.observ_id)
                self.sit_relev.append(observ.relevance2)

                # append the sentence to the article
                self.content += f"{observ.observation_new} "
                print(observ.year, observ.week_number, observ.day_number, observ.pattern, observ.observation_new)

            # end of paragraph (add a paragraph divider)
            self.content += self.par_divider
            print(self.par_divider)
