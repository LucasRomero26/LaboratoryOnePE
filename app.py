import streamlit as st
import numpy as np
import pandas as pd

def calculate_ybus(n_nodes, branches):
    """
    Matriz Ybus considerando impedancias y admitancias shunt (Y/2).
    
    Parámetros:
      - n_nodes: Número de nodos del sistema (excluyendo tierra).
      - branches: Lista de diccionarios que representan las ramas del sistema, cada una con:
          - 'from': nodo de inicio (números enteros iniciando en 1)
          - 'to': nodo final (0 para tierra, o un número de 1 a n_nodes)
          - 'resistance': resistencia de la rama
          - 'reactance': reactancia de la rama
          - 'y_shunt_imag': parte imaginaria de la admitancia shunt (Y/2)
    
    Retorna:
      - Matriz Ybus calculada (numpy.ndarray de números complejos).
    """

    Ybus = np.zeros((n_nodes, n_nodes), dtype=complex)
    
    for branch in branches:
        i = branch['from'] - 1  # Ajuste de índice para Python (0-indexado)
        j = branch['to'] - 1 if branch['to'] != 0 else None  # Si es tierra, j es None
        Z = complex(branch['resistance'], branch['reactance'])  # Impedancia
        Y = 1 / Z if Z != 0 else 0  # Admitancia (evita división por 0)
        
        if j is not None:  # Conexión entre dos nodos
            Ybus[i, i] += Y
            Ybus[j, j] += Y
            Ybus[i, j] -= Y
            Ybus[j, i] -= Y
        else:  # Conexión a tierra (nodo 0)
            Ybus[i, i] += Y
        
        # Agregar admitancia shunt Y/2 en los extremos 
        Y_shunt = complex(0, branch['y_shunt_imag'])
        Ybus[i, i] += Y_shunt
        if j is not None:
            Ybus[j, j] += Y_shunt
    
    return Ybus

def format_complex(z):
    """Formatea un número complejo a cadena con cinco cifras significativas."""
    if z.imag >= 0:
        return f"{z.real:.5f} + {z.imag:.5f}j"
    else:
        return f"{z.real:.5f} - {abs(z.imag):.5f}j"

def main():
    st.title("Cálculo de la Matriz Ybus con Impedancias")
    st.write("Este programa calcula la matriz Ybus de un sistema eléctrico de potencia basado en las impedancias de las líneas. Permite conexiones a tierra (nodo 0).")
    
    # Entrada de parámetros del sistema
    n_nodes = st.number_input("Ingrese el número de nodos (excluyendo tierra):", min_value=2, step=1, value=3)
    n_branches = st.number_input("Ingrese el número de ramas:", min_value=1, step=1, value=2)
    
    st.write("Ingrese los datos de cada línea:")
    with st.form("branch_form"):
        branch_data = []
        
        for i in range(int(n_branches)):
            st.markdown(f"**Línea {i+1}**")
            col1, col2, col3, col4, col5 = st.columns(5)
            from_node = col1.number_input("Nodo inicial", min_value=1, max_value=int(n_nodes), step=1, key=f"from_{i}")
            to_node = col2.number_input("Nodo final (0 para tierra)", min_value=0, max_value=int(n_nodes), step=1, key=f"to_{i}")
            resistance = col3.number_input("Resistencia (Ω)", step=0.00001, format="%.5f", key=f"res_{i}")
            reactance = col4.number_input("Reactancia (Ω)", step=0.00001, format="%.5f", key=f"react_{i}")
            y_shunt_imag = col5.number_input("Y/2 (parte imaginaria)", step=0.00001, format="%.5f", key=f"yshunt_imag_{i}")
            
            branch_data.append({
                'from': from_node,
                'to': to_node,
                'resistance': resistance,
                'reactance': reactance,
                'y_shunt_imag': y_shunt_imag
            })
        
        submitted = st.form_submit_button("Calcular Ybus")
        if submitted:
            # Validación de las entradas
            valid = True
            for branch in branch_data:
                if branch['from'] == branch['to'] and branch['to'] != 0:
                    st.error("El nodo inicial y final no pueden ser iguales, a menos que sea conexión a tierra.")
                    valid = False
                if branch['from'] == 0:
                    st.error("El nodo inicial no puede ser 0 (tierra).")
                    valid = False
            
            if valid:
                Ybus = calculate_ybus(int(n_nodes), branch_data)
                st.write("La matriz Ybus calculada es:")
                
                # Formateo de la matriz para mostrar cada elemento como un complejo con cinco decimales
                formatted_matrix = [
                    [format_complex(Ybus[i, j]) for j in range(Ybus.shape[1])] 
                    for i in range(Ybus.shape[0])
                ]
                df_matrix = pd.DataFrame(
                    formatted_matrix, 
                    columns=[f"Nodo {i+1}" for i in range(n_nodes)], 
                    index=[f"Nodo {i+1}" for i in range(n_nodes)]
                )
                st.table(df_matrix)

    st.markdown("## Explicación paso a paso del código")
    st.markdown("""
    1. **Cálculo de la matriz Ybus:**  
       - La función `calculate_ybus` crea una matriz de ceros complejos.
       - Para cada rama:
         - Si el nodo final no es 0, se suma la admitancia a las diagonales de ambos nodos y se resta en las posiciones fuera de la diagonal.
         - Si el nodo final es 0 (tierra), solo se suma la admitancia a la diagonal del nodo inicial.
       - Se agrega la admitancia shunt (Y/2) a las diagonales correspondientes.

    2. **Interfaz en Streamlit:**  
       - El usuario ingresa el número de nodos y ramas.
       - Por cada rama, se especifican el nodo inicial (de 1 a n_nodes), el nodo final (0 para tierra o de 1 a n_nodes), la resistencia, la reactancia y la admitancia shunt.

    3. **Validación:**  
       - Se verifica que el nodo inicial no sea 0 y que los nodos inicial y final no sean iguales, salvo en conexiones a tierra.

    4. **Presentación de Resultados:**  
       - La matriz Ybus se muestra en una tabla con números complejos formateados a cinco decimales.
    """)

if __name__ == "__main__":
    main()