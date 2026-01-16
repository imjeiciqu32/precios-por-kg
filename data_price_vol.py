# --- DATOS PARA MODO PRICE AND VOLUMEN ---
# Lo envolvemos en un diccionario para que .keys() funcione y el selectbox lo reconozca
PLANTILLA_PV = {
    "Ventas Históricas Takis": [
        {"Semana": 1, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5120, "Venta Valor ($)": 92160.00},
        {"Semana": 2, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 4980, "Venta Valor ($)": 90138.00},
        {"Semana": 3, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5200, "Venta Valor ($)": 93340.00},
        {"Semana": 4, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5050, "Venta Valor ($)": 90900.00},
        {"Semana": 5, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 4900, "Venta Valor ($)": 88445.00},
        {"Semana": 6, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5100, "Venta Valor ($)": 91800.00},
        {"Semana": 7, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5080, "Venta Valor ($)": 91440.00},
        {"Semana": 8, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 4750, "Venta Valor ($)": 86450.00},
        {"Semana": 9, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5150, "Venta Valor ($)": 92700.00},
        {"Semana": 10, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5400, "Venta Valor ($)": 96120.00},
        {"Semana": 11, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 8200, "Venta Valor ($)": 127100.00},
        {"Semana": 12, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 8500, "Venta Valor ($)": 131750.00},
        {"Semana": 13, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 7900, "Venta Valor ($)": 123240.00},
        {"Semana": 14, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 5020, "Venta Valor ($)": 90360.00},
        {"Semana": 15, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 18.00, "Venta Volumen (Pzas)": 4950, "Venta Valor ($)": 89100.00},
        {"Semana": 16, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 4600, "Venta Valor ($)": 85100.00},
        {"Semana": 17, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 4550, "Venta Valor ($)": 84175.00},
        {"Semana": 18, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 4620, "Venta Valor ($)": 85470.00},
        {"Semana": 19, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 4580, "Venta Valor ($)": 84730.00},
        {"Semana": 20, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 4200, "Venta Valor ($)": 79800.00},
        {"Semana": 21, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 4150, "Venta Valor ($)": 78850.00},
        {"Semana": 22, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 3800, "Venta Valor ($)": 74100.00},
        {"Semana": 23, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 3750, "Venta Valor ($)": 73125.00},
        {"Semana": 24, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 3400, "Venta Valor ($)": 68000.00},
        {"Semana": 25, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 3350, "Venta Valor ($)": 67000.00},
        {"Semana": 26, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 3100, "Venta Valor ($)": 63550.00},
        {"Semana": 27, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 3050, "Venta Valor ($)": 62525.00},
        {"Semana": 28, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 2800, "Venta Valor ($)": 58800.00},
        {"Semana": 29, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 2750, "Venta Valor ($)": 57750.00},
        {"Semana": 30, "Producto": "Takis Fuego 70g", "Fabricante": "BARCEL", "Precio ($)": 20.00, "Venta Volumen (Pzas)": 2700, "Venta Valor ($)": 56700.00}
    ],
    "Ventas Históricas Chips": [
        # ENERO | Venta Mes: 161,641 | Pzas Mes: 169,017
        {"Semana": 1, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 169017, "Venta Valor ($)": 161641.00},
        {"Semana": 2, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 169017, "Venta Valor ($)": 161641.00},
        {"Semana": 3, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 169017, "Venta Valor ($)": 161641.00},
        {"Semana": 4, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 169017, "Venta Valor ($)": 161641.00},

        # FEBRERO | Venta Mes: 146,134 | Pzas Mes: 150,788
        {"Semana": 5, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.97, "Venta Volumen (Pzas)": 150788, "Venta Valor ($)": 146134.00},
        {"Semana": 6, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.97, "Venta Volumen (Pzas)": 150788, "Venta Valor ($)": 146134.00},
        {"Semana": 7, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.97, "Venta Volumen (Pzas)": 150788, "Venta Valor ($)": 146134.00},
        {"Semana": 8, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.97, "Venta Volumen (Pzas)": 150788, "Venta Valor ($)": 146134.00},

        # MARZO | Venta Mes: 149,225 | Pzas Mes: 152,570
        {"Semana": 9, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.98, "Venta Volumen (Pzas)": 152570, "Venta Valor ($)": 149225.00},
        {"Semana": 10, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.98, "Venta Volumen (Pzas)": 152570, "Venta Valor ($)": 149225.00},
        {"Semana": 11, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.98, "Venta Volumen (Pzas)": 152570, "Venta Valor ($)": 149225.00},
        {"Semana": 12, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.98, "Venta Volumen (Pzas)": 152570, "Venta Valor ($)": 149225.00},

        # ABRIL | Venta Mes: 157,270 | Pzas Mes: 163,747
        {"Semana": 13, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 163747, "Venta Valor ($)": 157270.00},
        {"Semana": 14, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 163747, "Venta Valor ($)": 157270.00},
        {"Semana": 15, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 163747, "Venta Valor ($)": 157270.00},
        {"Semana": 16, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.96, "Venta Volumen (Pzas)": 163747, "Venta Valor ($)": 157270.00},

        # MAYO | Venta Mes: 160,603 | Pzas Mes: 172,236
        {"Semana": 17, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 172236, "Venta Valor ($)": 160603.00},
        {"Semana": 18, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 172236, "Venta Valor ($)": 160603.00},
        {"Semana": 19, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 172236, "Venta Valor ($)": 160603.00},
        {"Semana": 20, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 172236, "Venta Valor ($)": 160603.00},

        # JUNIO | Venta Mes: 128,522 | Pzas Mes: 136,777
        {"Semana": 21, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.94, "Venta Volumen (Pzas)": 136777, "Venta Valor ($)": 128522.00},
        {"Semana": 22, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.94, "Venta Volumen (Pzas)": 136777, "Venta Valor ($)": 128522.00},
        {"Semana": 23, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.94, "Venta Volumen (Pzas)": 136777, "Venta Valor ($)": 128522.00},
        {"Semana": 24, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.94, "Venta Volumen (Pzas)": 136777, "Venta Valor ($)": 128522.00},

        # JULIO | Venta Mes: 148,433 | Pzas Mes: 159,770
        {"Semana": 25, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 159770, "Venta Valor ($)": 148433.00},
        {"Semana": 26, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 159770, "Venta Valor ($)": 148433.00},
        {"Semana": 27, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 159770, "Venta Valor ($)": 148433.00},
        {"Semana": 28, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.93, "Venta Volumen (Pzas)": 159770, "Venta Valor ($)": 148433.00},

        # AGOSTO | Venta Mes: 136,838 | Pzas Mes: 150,203
        {"Semana": 29, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.91, "Venta Volumen (Pzas)": 150203, "Venta Valor ($)": 136838.00},
        {"Semana": 30, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.91, "Venta Volumen (Pzas)": 150203, "Venta Valor ($)": 136838.00},
        {"Semana": 31, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.91, "Venta Volumen (Pzas)": 150203, "Venta Valor ($)": 136838.00},
        {"Semana": 32, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.91, "Venta Volumen (Pzas)": 150203, "Venta Valor ($)": 136838.00},

        # SEPTIEMBRE | Venta Mes: 148,493 | Pzas Mes: 164,960
        {"Semana": 33, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 164960, "Venta Valor ($)": 148493.00},
        {"Semana": 34, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 164960, "Venta Valor ($)": 148493.00},
        {"Semana": 35, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 164960, "Venta Valor ($)": 148493.00},
        {"Semana": 36, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 164960, "Venta Valor ($)": 148493.00},

        # OCTUBRE | Venta Mes: 169,104 | Pzas Mes: 186,904
        {"Semana": 37, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 186904, "Venta Valor ($)": 169104.00},
        {"Semana": 38, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 186904, "Venta Valor ($)": 169104.00},
        {"Semana": 39, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 186904, "Venta Valor ($)": 169104.00},
        {"Semana": 40, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 0.90, "Venta Volumen (Pzas)": 186904, "Venta Valor ($)": 169104.00},

        # NOVIEMBRE | Venta Mes: 167,453 | Pzas Mes: 166,601
        {"Semana": 41, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.01, "Venta Volumen (Pzas)": 166601, "Venta Valor ($)": 167453.00},
        {"Semana": 42, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.01, "Venta Volumen (Pzas)": 166601, "Venta Valor ($)": 167453.00},
        {"Semana": 43, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.01, "Venta Volumen (Pzas)": 166601, "Venta Valor ($)": 167453.00},
        {"Semana": 44, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.01, "Venta Volumen (Pzas)": 166601, "Venta Valor ($)": 167453.00},

        # DICIEMBRE | Venta Mes: 182,951 | Pzas Mes: 178,861
        {"Semana": 45, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.02, "Venta Volumen (Pzas)": 178861, "Venta Valor ($)": 182951.00},
        {"Semana": 46, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.02, "Venta Volumen (Pzas)": 178861, "Venta Valor ($)": 182951.00},
        {"Semana": 47, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.02, "Venta Volumen (Pzas)": 178861, "Venta Valor ($)": 182951.00},
        {"Semana": 48, "Producto": "CHIPS 36", "Fabricante": "BARCEL", "Precio ($)": 1.02, "Venta Volumen (Pzas)": 178861, "Venta Valor ($)": 182951.00},
    ]
}
