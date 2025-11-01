
import math
import ezdxf
import numpy as np


class Calculator():
    def __init__(self):
        self.i = 17
        self.dsh = 6
        self.Rout = 38
        self.D = 90
        self.u = 1      # Число волн, создаваемых волнообразователем (НЕ ТРОГАТЬ, т.к для более чем 1 не расчитывалось)
        self.RESOLUTION = 600
        self.BASE_WHEEL_SHAPE = True
        self.SEPARATOR = True
        self.ECCENTRIC = True
        self.BALLS = False
        self.OUT_DIAMETER = True
        self.parameters_txt_ru = """Нет данных"""
        self.parameters_txt_en = """No data"""
        self.__error_ru = None
        self.__error_en = None
        self.generated = False

    def set_args(self, i, dsh, Rout, D, RESOLUTION, BASE_WHEEL_SHAPE, ECCENTRIC, SEPARATOR, BALLS,  OUT_DIAMETER):
        self.i = int(i)
        self.dsh = float(dsh)
        if Rout == "":
            self.Rout = 0
        else:
            self.Rout = float(Rout)
        if D == "":
            self.D = 0
        else:
            self.D = float(D)
        self.RESOLUTION = int(RESOLUTION)
        self.BASE_WHEEL_SHAPE = self.get_bool(BASE_WHEEL_SHAPE)
        self.SEPARATOR = self.get_bool(SEPARATOR)
        self.ECCENTRIC = self.get_bool(ECCENTRIC)
        self.BALLS = self.get_bool(BALLS)
        self.OUT_DIAMETER = self.get_bool(OUT_DIAMETER)

    def generate(self):
        e = 0.2 * self.dsh
        zg = (self.i + 1) * self.u
        zsh = self.i
        rsh = self.dsh / 2
        hc = 2.2 * e

        if not self.Rout:
            Rin = math.ceil(((1.03 * self.dsh) / np.sin(np.pi / zg)) * 1000) / 1000     # умножение и деление на 1000 нужно для округления в бОльшую сторону до 3-х знаков после точки
            self.Rout = Rin + 2 * e
        else:
            Rin = self.Rout - 2 * e

        rd = Rin + e - self.dsh
        Rsep_m = rd + rsh
        Rsep_out = Rsep_m + hc / 2
        Rsep_in = Rsep_m - hc / 2

        if Rin <= ((1.03 * self.dsh) / np.sin(np.pi / zg)):
            self.parameters_txt_ru = """Нет данных"""
            self.parameters_txt_en = """No data"""
            self.__error_ru = """Внутренний радиус впадин жесткого колеса (Rin = {0} мм) должен быть больше: {1} мм. 
Увеличьте Rout или уменьшите передаточное число (i)""".format(Rin, (1.03 * self.dsh) / np.sin(np.pi / zg))
            self.__error_en = """The inner radius of the recesses of the rigid wheel (Rin = {0} mm) must be greater than: {1} mm. 
Increase the Rout or decrease the gear ratio (i)""".format(Rin, (1.03 * self.dsh) / np.sin(np.pi / zg))
            return None
        if 0 < self.D <= self.Rout * 2:
            self.parameters_txt_ru = """Нет данных"""
            self.parameters_txt_en = """No data"""
            self.__error_ru = """Внешний диаметр редуктора должен быть больше, чем 2 * внешний радиус впадин жесткого колеса. 
Если вам не нужна внешняя окружность - не заполняйте поле с данным параметром"""
            self.__error_en = """This parameter must be greater than 2 * outer radius of the recesses of the hard wheel.
If you do not need an outer circle, do not fill in the field with this parameter."""
            return None
        self.__error_ru = None
        self.__error_en = None

        self.parameters_txt_ru = f"""Основные параметры ВПТК:
    - Передаточное число:       {self.i}
    - Эксцентриситет:           {e}
    - Радиус эксцентрика:       {rd}
    - Внешний радиус профиля жесткого колеса:       {self.Rout}
    - Внутренний радиус профиля жесткого колеса:    {Rin}
    - Число впадин профиля жесткого колеса:         {zg}
    - Число шариков (роликов):              {zsh}
    - Диаметр шариков (роликов):            {self.dsh}
    - Делительный радиус сепаратора:        {Rsep_m}
    - Толщина сепаратора:                   {hc}
    - Внешний диаметр редуктора:            {self.D} """

        self.parameters_txt_en = f"""The main parameters of the transmission:
    - Gear ratio:               {self.i}
    - The eccentricity:         {e}
    - Radius of the eccentric:  {rd}
    - The outer radius of the hard wheel profile:           {self.Rout}
    - The inner radius of the rigid wheel profile:          {Rin}
    - Number of recesses in the profile of the hard wheel:  {zg}
    - Number of balls (rollers):           {zsh}
    - Diameter of the balls (rollers):     {self.dsh}
    - Dividing radius of the separator:    {Rsep_m}
    - Separator thickness:                 {hc}
    - The outer diameter of the gearbox:   {self.D} """

        theta = np.linspace(0, 2 * np.pi, self.RESOLUTION)

        S = np.sqrt((rsh + rd) ** 2 - np.power(e * np.sin(zg * theta), 2))
        l = e * np.cos(zg * theta) + S
        Xi = np.arctan2(e * zg * np.sin(zg * theta), S)

        x = l * np.sin(theta) + rsh * np.sin(theta + Xi)
        y = l * np.cos(theta) + rsh * np.cos(theta + Xi)

        xy = np.stack((x, y), axis=1)

        sh_angle = np.linspace(0, 1, zsh + 1) * 2 * np.pi
        S_sh = np.sqrt((rsh + rd) ** 2 - np.power(e * np.sin(zg * sh_angle), 2))
        l_Sh = e * np.cos(zg * sh_angle) + S_sh
        x_sh = l_Sh * np.sin(sh_angle)
        y_sh = l_Sh * np.cos(sh_angle)

        self.__doc = ezdxf.new("R2000")
        msp = self.__doc.modelspace()

        if self.BASE_WHEEL_SHAPE:
            msp.add_point([0, 0])
            msp.add_lwpolyline(xy)

        if self.SEPARATOR:
            msp.add_circle((0, 0), radius=Rsep_out)
            msp.add_circle((0, 0), radius=Rsep_in)

        if self.ECCENTRIC:
            msp.add_point([0, e])
            msp.add_lwpolyline([[0, 0], [0, e]])
            msp.add_lwpolyline([[-6, 0], [6, 0]])
            msp.add_lwpolyline([[-3, e], [3, e]])
            msp.add_circle((0, e), radius=rd)

        if self.BALLS:
            for i in range(zsh):
                msp.add_circle((x_sh[i], y_sh[i]), radius=rsh)

        if self.OUT_DIAMETER and self.D:
            msp.add_circle((0, 0), radius=self.D / 2)

        self.generated = True


    def save_dxf(self, filename):
        self.__doc.saveas(filename + ".dxf")

    def save_txt(self, filename, language):
        self.__txt = open(filename + ".txt", "w")
        if language == "ru":
            print(self.parameters_txt_ru, file=self.__txt)
        elif language == "en":
            print(self.parameters_txt_en, file=self.__txt)
        self.__txt.close()

    def get_parameters_string(self, language):
        if language == "ru":
            return self.parameters_txt_ru
        elif language == "en":
            return self.parameters_txt_en

    def get_error(self, language):
        if language == "ru":
            return self.__error_ru
        elif language == "en":
            return self.__error_en


    @staticmethod
    def get_bool(arg):
        if arg == "on": return True
        return False

