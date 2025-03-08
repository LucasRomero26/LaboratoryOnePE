import streamlit as st
import numpy as np
import pandas as pd

def calculate_ybus(n_nodes, branches):
    """
    Matriz Ybus considerando impedancias y admitancias shunt en nodos extremos.
    """
    Ybus = np.zeros((n_nodes, n_nodes), dtype=complex)
    
    for branch in branches:
        i = branch['from'] - 1  # Ajuste de índice para Python (0-indexado)
        j = branch['to'] - 1
        Z = complex(branch['resistance'], branch['reactance'])  # Impedancia
        Y = 1 / Z if Z != 0 else 0  # Admitancia (evita división por 0)
        
        Ybus[i, i] += Y
        Ybus[j, j] += Y
        Ybus[i, j] -= Y
        Ybus[j, i] -= Y
        
        # Agregar admitancia shunt según ubicación seleccionada
        if branch['y_shunt_loc'] == "Inicio" or branch['y_shunt_loc'] == "Ambos":
            Ybus[i, i] += complex(0, branch['y_shunt_imag'])
        if branch['y_shunt_loc'] == "Final" or branch['y_shunt_loc'] == "Ambos":
            Ybus[j, j] += complex(0, branch['y_shunt_imag'])
    
    return Ybus

def format_complex(z):
    """ Formatea un número complejo a cadena con cinco cifras significativas. """
    if z.imag >= 0:
        return f"{z.real:.5f} + {z.imag:.5f}j"
    else:
        return f"{z.real:.5f} - {abs(z.imag):.5f}j"

def main():
    st.title("Cálculo de la Matriz Ybus con Impedancias")
    st.write("Este programa calcula la matriz Ybus de un sistema eléctrico de potencia basado en las impedancias de las líneas.")
    
    n_nodes = st.number_input("Ingrese el número de nodos:", min_value=2, step=1, value=3)
    n_branches = st.number_input("Ingrese el número de ramas:", min_value=1, step=1, value=2)
    
    st.write("Ingrese los datos de cada línea:")
    with st.form("branch_form"):
        branch_data = []
        
        for i in range(int(n_branches)):
            st.markdown(f"**Línea {i+1}**")
            col1, col2, col3, col4, col5, col6 = st.columns(6)
            from_node = col1.number_input("Nodo inicial", min_value=1, max_value=int(n_nodes), step=1, key=f"from_{i}")
            to_node = col2.number_input("Nodo final", min_value=1, max_value=int(n_nodes), step=1, key=f"to_{i}")
            resistance = col3.number_input("Resistencia (Ω)", step=0.00001, format="%.5f", key=f"res_{i}")
            reactance = col4.number_input("Reactancia (Ω)", step=0.00001, format="%.5f", key=f"react_{i}")
            y_shunt_imag = col5.number_input("Admitancia shunt (Imaginaria)", step=0.00001, format="%.5f", key=f"yshunt_imag_{i}")
            y_shunt_loc = col6.selectbox("Ubicación Yshunt", ["Ninguno", "Inicio", "Final", "Ambos"], key=f"yshunt_loc_{i}")
            
            branch_data.append({
                'from': from_node,
                'to': to_node,
                'resistance': resistance,
                'reactance': reactance,
                'y_shunt_imag': y_shunt_imag,
                'y_shunt_loc': y_shunt_loc
            })
        
        submitted = st.form_submit_button("Calcular Ybus")
        if submitted:
            valid = all(branch['from'] != branch['to'] for branch in branch_data)
            if not valid:
                st.error("El nodo inicial y final no pueden ser iguales en una línea.")
            else:
                Ybus = calculate_ybus(int(n_nodes), branch_data)
                st.write("La matriz Ybus calculada es:")
                
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

if __name__ == "__main__":
    main()
