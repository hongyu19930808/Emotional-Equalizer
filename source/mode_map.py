class Mode:

    @staticmethod
    def get_mode_map(mode):
        if mode == 'Major':
            mode_map = Mode.get_major_map()
        elif mode == 'Natural Minor' or mode == 'Minor':
            mode_map = Mode.get_natural_minor_map()   
        elif mode == 'Harmonic Minor':
            mode_map = Mode.get_harmonic_minor_map()
        else:
            mode_map = None
        return mode_map    

    @staticmethod
    def get_major_map():
        major_map = {1: 0, 1.5: 1, 
                     2: 2, 2.5: 3,
                     3: 4, 3.5: 4, 
                     4: 5, 4.5: 6,
                     5: 7, 5.5: 8, 
                     6: 9, 6.5: 10,
                     7: 11, 7.5: 11, 
                     'name': 'Major'}
        return major_map
    
    @staticmethod
    def get_natural_minor_map():
        natural_minor_map = {1: 0, 1.5: 1, 
                             2: 2, 2.5: 2,
                             3: 3, 3.5: 4, 
                             4: 5, 4.5: 6,
                             5: 7, 5.5: 7, 
                             6: 8, 6.5: 9,
                             7: 10, 7.5: 11, 
                             'name': 'Minor'}
        return natural_minor_map
    
    @staticmethod
    def get_harmonic_minor_map():
        harmonic_minor_map = {1: 0, 1.5: 1, 
                              2: 2, 2.5: 2,
                              3: 3, 3.5: 4, 
                              4: 5, 4.5: 6,
                              5: 7, 5.5: 7, 
                              6: 8, 6.5: 9,
                              7: 11, 7.5: 11, 
                              'name': 'Minor'}
        return harmonic_minor_map
