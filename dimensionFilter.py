import re
from draw import BOX_UNIT
from math import floor

ONE_DECIMAL_TOL = 0.5
TWO_DECIMAL_TOL = 0.15
THREE_DECIMAL_TOL = 0.05
LTCURVE_LIMIT = 400

class Dimension:
    def __init__(self, figure_type, page, string, label, x1, y1, x2, y2, nom, tol, copy=1):
        self.type = figure_type
        self.page_number = page
        self.string = string
        self.label = label
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.nominal = nom
        self.tolerance = tol
        self.copies = copy

    @classmethod
    def file_input(cls, figure_type):
        return cls(figure_type, 0, "", "", 0, 0, 0, 0, "", "", 1)

    @classmethod
    def copy_dim(cls, dim):
        return cls(dim.type, dim.page_number, "", "", dim.x1, str(float(dim.y1)-BOX_UNIT), dim.x2, str(float(dim.y2)-BOX_UNIT), "", "", 1)

    def string_parser(self):
        if "±" in self.string:
            separator = self.string.index("±")
            self.nominal = self.string[0:separator]
            self.tolerance = self.string[separator+1:]
        elif re.search('[A-E]', self.string):
            self.nominal = re.sub("[^0123456789\.]", "", self.string)
            self.tolerance = "-"
        elif "°" in self.string:
            self.nominal = self.string
            self.tolerance = '0.5°'
        elif "." in self.string:
            self.nominal = re.sub("[^0123456789\.]", "", self.string)
            decimals = len(self.nominal) - self.nominal.index(".") - 1
            if decimals == 1:
                self.tolerance = ONE_DECIMAL_TOL
            elif decimals == 2:
                self.tolerance = TWO_DECIMAL_TOL
            elif decimals == 3:
                self.tolerance = THREE_DECIMAL_TOL
            else:
                return
        else:
            raise SystemExit("Cancelled: string parsing error occurred")

    def validate_dimension(self):
        if self.type == "LTTextBoxHorizontal" or self.type == "LTTextBoxVertical":  # If a text box
            if has_numbers(self.string):                                            # If contains numbers
                if re.search('[a-zE-QS-WY-Z]', self.string):
                    return 0
                self.string = re.sub("[^0123456789ABCDEX±°\.]", "", self.string)
                if self.string == "":
                    return 0
                elif self.string[-1] == ".":
                    return 0
                elif "0.5" in self.string and "0.15" in self.string and "0.05" in self.string:
                    return 0
                elif "X" in self.string:
                    if "." in self.string:
                        self.string = self.string.lstrip()
                        self.copies = int(self.string[0])
                        self.string = self.string[self.string.index("X")+1:]
                        return 1
                    else:
                        number = int(self.string[len(self.string) - len(self.string.lstrip())])
                        return number                                                   # Return number of dims
                elif "." in self.string:
                    return 1                                                        # Return 1 dim
                elif "±" in self.string:
                    return 1
                elif "°" in self.string:
                    return 1
                else:
                    return 0
            else:
                return 0
        elif self.type == "LTLine" or self.type == "LTFigure" or (abs(float(self.y1) - float(self.y2)) < LTCURVE_LIMIT and abs(float(self.x1) - float(self.x2)) < LTCURVE_LIMIT) :
            return 0
        else:
            return -1                                                             # Return -1 for invalid dimension


def file_input(p_file, dim_array=[], objects=[], mapped_matrix = []):
    page_no = False
    coordinate = False
    next_copy = False

    for line in p_file:             # inputs file into array of Dimension objects
        line = line.strip()
        if page_no:
            page_no = False
            coordinate = True
            dim_array[-1].page_number = int(line)
        elif coordinate:
            coordinate = False
            line = line.strip("( )")
            dim_array[-1].x1, dim_array[-1].y1, dim_array[-1].x2, dim_array[-1].y2 = line.split(",")
        elif "LTText" in line or "LTLine" in line or "LTFigure" in line or "LTCurve" in line:
            dim = Dimension.file_input(line)
            dim_array.append(dim)
            page_no = True
            next_copy = False
        elif next_copy:
            dim = Dimension.copy_dim(dim_array[-1])
            dim.string = line
            dim_array.append(dim)
        elif line == "\n":
            continue
        else:
            dim_array[-1].string = line
            next_copy = True

    copy_number = 1
    for dimension in dim_array[:]:
        number = dimension.validate_dimension()
        if number > -1:
            x = floor(float(dimension.x1)/BOX_UNIT)
            x_limit = floor(float(dimension.x2)/BOX_UNIT)
            y_limit = floor(float(dimension.y2)/BOX_UNIT)
            while x <= x_limit:
                y = floor(float(dimension.y1)/BOX_UNIT)
                while y <= y_limit:
                    try:
                        mapped_matrix[x][y] = True
                        print("True")
                    except IndexError:
                        print("Index error: ", x, ", ", y)
                    y += 1
                x += 1
        if number == -1:
            dim_array.remove(dimension)
        elif number == 0:  # lines or text
            objects.append(dimension)
            dim_array.remove(dimension)
        elif copy_number > 1:
            dimension.copies = copy_number
            dimension.string_parser()
            copy_number = 1
        elif number == 1:  # dimension
            dimension.string_parser()
        else:  # 2X
            copy_number = number
            objects.append(dimension)
            dim_array.remove(dimension)


def has_numbers(input_string):
    return any(char.isdigit() for char in input_string)


