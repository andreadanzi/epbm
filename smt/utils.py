def toFloat(s):
        try:
            s=float(s)
        except ValueError:
            pass 
        except TypeError:
            pass             
        return s