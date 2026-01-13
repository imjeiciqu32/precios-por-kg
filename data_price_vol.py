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
    ]
}
