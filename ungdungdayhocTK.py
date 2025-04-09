import streamlit as st
import pandas as pd
import plotly.express as px

# Hàm tính toán tần số với sắp xếp từ bé đến lớn
def calculate_frequency(data):
    flat_data = [item for sublist in data for item in sublist if item.strip()] if isinstance(data[0], list) else [item for item in data if item.strip()]
    if not flat_data:
        return [], [], 0, []
    
    unique_values_raw = list(set(flat_data))
    
    sortable_values = []
    for val in unique_values_raw:
        try:
            num_val = float(val)
            sortable_values.append(num_val if num_val != int(num_val) else int(num_val))
        except ValueError:
            sortable_values.append(val)
    
    sorted_pairs = sorted(zip(sortable_values, unique_values_raw))
    unique_values = [pair[1] for pair in sorted_pairs]
    
    frequencies = [flat_data.count(val) for val in unique_values]
    total_count = len(flat_data)
    relative_frequencies = [freq / total_count * 100 for freq in frequencies]
    
    formatted_values = []
    for val in unique_values:
        try:
            num_val = float(val)
            formatted_values.append(int(num_val) if num_val.is_integer() else num_val)
        except ValueError:
            formatted_values.append(val)
    
    return formatted_values, frequencies, total_count, relative_frequencies

# Tiêu đề ứng dụng
st.title("Ứng dụng Nhập liệu và Thống kê")

# Tạo các tab
tab1, tab2, tab3 = st.tabs(["Nhập liệu và Tạo bảng", "Biểu đồ Tần số", "Biểu đồ Tần số Tương đối"])

with tab1:
    st.subheader("Nhập Liệu")
    
    input_method = st.selectbox("Chọn cách nhập liệu:", ["Nhập liệu thông thường", "Nhập liệu từ bảng tần số"])
    
    if 'input_data' not in st.session_state:
        st.session_state['input_data'] = []
    if 'frequency_values' not in st.session_state:
        st.session_state['frequency_values'] = [None] * 3  # Giá trị
    if 'frequency_counts' not in st.session_state:
        st.session_state['frequency_counts'] = [0] * 3  # Tần số
    if 'num_columns' not in st.session_state:
        st.session_state['num_columns'] = 3  # Số cột mặc định cho bảng tần số
    if 'edit_mode' not in st.session_state:
        st.session_state['edit_mode'] = True
    if 'data_type' not in st.session_state:
        st.session_state['data_type'] = None
    if 'normal_num_cols' not in st.session_state:
        st.session_state['normal_num_cols'] = 5  # Số cột mặc định ban đầu
    if 'normal_num_rows' not in st.session_state:
        st.session_state['normal_num_rows'] = 3  # Số dòng mặc định ban đầu
    if 'frequency_table_transposed' not in st.session_state:
        st.session_state['frequency_table_transposed'] = False  # Trạng thái hiển thị bảng thống kê tần số (dọc hay ngang)
    if 'show_frequency_table' not in st.session_state:
        st.session_state['show_frequency_table'] = False  # Trạng thái hiển thị bảng thống kê tần số

    # Nhập liệu thông thường
    if input_method == "Nhập liệu thông thường":
        st.write("Nhập liệu thông thường")
        
        # Số cột và số dòng hiện tại
        num_cols = st.session_state['normal_num_cols']
        num_rows = st.session_state['normal_num_rows']
        
        # Khởi tạo dữ liệu nếu chưa có hoặc không khớp với kiểu dữ liệu
        if not st.session_state['input_data'] or st.session_state['data_type'] != "normal":
            st.session_state['input_data'] = [[''] * num_cols for _ in range(num_rows)]
            st.session_state['data_type'] = "normal"
        
        if st.session_state['edit_mode']:
            # Cập nhật dữ liệu trước khi hiển thị
            current_data = st.session_state['input_data']
            # Đảm bảo dữ liệu có đúng số dòng và số cột
            if len(current_data) < num_rows:
                current_data.extend([''] * num_cols for _ in range(num_rows - len(current_data)))
            elif len(current_data) > num_rows:
                current_data = current_data[:num_rows]
            
            for i in range(len(current_data)):
                if len(current_data[i]) < num_cols:
                    current_data[i].extend([''] * (num_cols - len(current_data[i])))
                elif len(current_data[i]) > num_cols:
                    current_data[i] = current_data[i][:num_cols]
            
            st.session_state['input_data'] = current_data
            input_df = pd.DataFrame(st.session_state['input_data'])
            columns = [f"Cột {i+1}" for i in range(num_cols)]
            edited_df = st.data_editor(
                input_df,
                column_config={col: st.column_config.TextColumn(col) for col in columns},
                num_rows="fixed",  # Tắt tính năng thêm dòng tự động
                key="data_editor_normal"
            )
            st.session_state['temp_data'] = edited_df.values.tolist()
            
            # Sắp xếp các nút nằm ngang: Thêm dòng, Thêm cột, Xóa toàn bộ dữ liệu, Lưu
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("Thêm dòng"):
                    st.session_state['normal_num_rows'] += 1
                    st.session_state['input_data'].append([''] * num_cols)
                    st.rerun()
            with col2:
                if st.button("Thêm cột"):
                    st.session_state['normal_num_cols'] += 1
                    for row in st.session_state['input_data']:
                        row.append('')
                    st.rerun()
            with col3:
                if st.button("Xóa toàn bộ dữ liệu"):
                    st.session_state['input_data'] = []
                    st.session_state['edit_mode'] = True
                    st.session_state['data_type'] = None
                    st.session_state['normal_num_cols'] = 5
                    st.session_state['normal_num_rows'] = 3
                    st.session_state['show_frequency_table'] = False
                    st.session_state['frequency_table_transposed'] = False
                    st.rerun()
            with col4:
                if st.button("Lưu"):
                    st.session_state['input_data'] = st.session_state['temp_data']
                    st.session_state['edit_mode'] = False
                    # Cập nhật số dòng và số cột dựa trên dữ liệu đã lưu
                    st.session_state['normal_num_rows'] = len(st.session_state['temp_data'])
                    st.session_state['normal_num_cols'] = len(st.session_state['temp_data'][0]) if st.session_state['temp_data'] else 5
                    st.rerun()
        
        if not st.session_state['edit_mode']:
            st.subheader("Bảng Dữ Liệu Đã Lưu")
            data_df = pd.DataFrame(st.session_state['input_data'])
            st.dataframe(data_df)
            
            # Sắp xếp các nút nằm ngang: Chỉnh Sửa Lại, Xóa toàn bộ dữ liệu
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Chỉnh Sửa Lại"):
                    st.session_state['edit_mode'] = True
                    st.rerun()
            with col2:
                if st.button("Xóa toàn bộ dữ liệu"):
                    st.session_state['input_data'] = []
                    st.session_state['edit_mode'] = True
                    st.session_state['data_type'] = None
                    st.session_state['normal_num_cols'] = 5
                    st.session_state['normal_num_rows'] = 3
                    st.session_state['show_frequency_table'] = False
                    st.session_state['frequency_table_transposed'] = False
                    st.rerun()
    
    # Nhập liệu từ bảng tần số
    elif input_method == "Nhập liệu từ bảng tần số":
        st.write("Nhập liệu từ bảng tần số (Nhập xong hết rồi nhấn Lưu)")
        
        # Số lượng cột hiện tại
        num_cols = st.session_state['num_columns']
        cols = st.columns(num_cols)
        
        # Nhập liệu cho từng cột
        for i in range(num_cols):
            with cols[i]:
                st.markdown(f"**Cột {i+1}**")
                # Nhập giá trị
                value = st.text_input(f"Giá trị {i+1}", value=st.session_state['frequency_values'][i] if st.session_state['frequency_values'][i] is not None else "", key=f"value_{i}")
                st.session_state['frequency_values'][i] = value
                # Nhập tần số
                frequency = st.number_input(f"Tần số {i+1}", min_value=0, value=st.session_state['frequency_counts'][i], step=1, key=f"freq_{i}")
                st.session_state['frequency_counts'][i] = frequency
        
        # Lọc các cột có dữ liệu hợp lệ
        valid_columns = []
        for i in range(num_cols):
            value = st.session_state['frequency_values'][i]
            frequency = st.session_state['frequency_counts'][i]
            if value is not None and value.strip() != "" and frequency > 0:
                valid_columns.append(i)
        
        # Hiển thị bảng chỉ với các cột hợp lệ
        if valid_columns:
            frequency_df = pd.DataFrame(
                [[st.session_state['frequency_values'][i] for i in valid_columns],
                 [st.session_state['frequency_counts'][i] for i in valid_columns]],
                index=["Giá trị", "Tần số"],
                columns=[f"Cột {i+1}" for i in valid_columns]
            )
            st.dataframe(frequency_df)
        else:
            st.info("Chưa có dữ liệu hợp lệ để hiển thị.")
        
        # Các nút điều khiển
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Lưu"):
                full_data = []
                for i in valid_columns:
                    value = st.session_state['frequency_values'][i]
                    frequency = st.session_state['frequency_counts'][i]
                    full_data.extend([str(value)] * int(frequency))
                if full_data:
                    st.session_state['input_data'] = full_data
                    st.session_state['data_type'] = "frequency"
                    st.rerun()
                else:
                    st.warning("Vui lòng nhập ít nhất một cặp giá trị-tần số hợp lệ.")
        with col2:
            if st.button("Thêm cột"):
                st.session_state['num_columns'] += 1
                st.session_state['frequency_values'].append(None)
                st.session_state['frequency_counts'].append(0)
                st.rerun()
        with col3:
            if st.button("Xóa toàn bộ dữ liệu"):
                st.session_state['num_columns'] = 3
                st.session_state['frequency_values'] = [None] * 3
                st.session_state['frequency_counts'] = [0] * 3
                st.session_state['input_data'] = []
                st.session_state['edit_mode'] = True
                st.session_state['data_type'] = None
                st.session_state['show_frequency_table'] = False
                st.session_state['frequency_table_transposed'] = False
                st.rerun()
    
    # Tính toán tần số và tạo bảng
    if st.button("Tính toán Tần số và Tạo Bảng"):
        if st.session_state['input_data']:
            if st.session_state['data_type'] == "normal":
                data_to_process = st.session_state['input_data']
            else:
                data_to_process = [[val] for val in st.session_state['input_data']]
            
            unique_values, frequencies, total_count, relative_frequencies = calculate_frequency(data_to_process)
            st.session_state['unique_values'] = unique_values
            st.session_state['frequencies'] = frequencies
            st.session_state['total_count'] = total_count
            st.session_state['relative_frequencies'] = relative_frequencies
            st.session_state['show_frequency_table'] = True
            st.session_state['frequency_table_transposed'] = False  # Mặc định hiển thị dạng ngang
            
            st.subheader("Bảng Thống kê Tần số")
            frequency_df = pd.DataFrame(
                [unique_values, frequencies, [f"{rf:.2f}%" for rf in relative_frequencies]],
                index=["Giá trị", "Tần số", "Tần số tương đối"]
            ).fillna('')
            st.session_state['frequency_df'] = frequency_df  # Lưu bảng để sử dụng lại
            st.dataframe(frequency_df)
            st.subheader("Cỡ Mẫu")
            st.markdown(f"**Cỡ mẫu là: {total_count} (N = {total_count})**")
        else:
            st.warning("Vui lòng nhập dữ liệu trước khi tính toán.")
    
    # Hiển thị nút chuyển đổi dạng bảng nếu bảng thống kê tần số đã được tạo
    if st.session_state.get('show_frequency_table', False):
        if not st.session_state['frequency_table_transposed']:
            if st.button("Chuyển bảng sang dạng dọc"):
                st.session_state['frequency_table_transposed'] = True
                st.rerun()
        else:
            if st.button("Chuyển về dạng ngang"):
                st.session_state['frequency_table_transposed'] = False
                st.rerun()
        
        # Hiển thị lại bảng thống kê tần số sau khi chuyển đổi
        if 'frequency_df' in st.session_state:
            st.subheader("Bảng Thống kê Tần số (Cập nhật)")
            frequency_df = st.session_state['frequency_df']
            if st.session_state['frequency_table_transposed']:
                frequency_df = frequency_df.transpose()
            st.dataframe(frequency_df)
            st.subheader("Cỡ Mẫu")
            st.markdown(f"**Cỡ mẫu là: {st.session_state['total_count']} (N = {st.session_state['total_count']})**")

with tab2:
    st.subheader("Biểu đồ Tần số")
    if 'unique_values' in st.session_state and st.session_state['unique_values']:
        fig_freq_bar = px.bar(x=st.session_state['unique_values'], y=st.session_state['frequencies'], labels={'x': 'Giá trị', 'y': 'Tần số'})
        st.plotly_chart(fig_freq_bar)
        fig_freq_line = px.line(x=st.session_state['unique_values'], y=st.session_state['frequencies'], labels={'x': 'Giá trị', 'y': 'Tần số'}, markers=True)
        st.plotly_chart(fig_freq_line)
    else:
        st.info("Vui lòng tính toán tần số ở tab 'Nhập liệu và Tạo bảng' trước.")

with tab3:
    st.subheader("Biểu đồ Tần số Tương đối")
    if 'unique_values' in st.session_state and st.session_state['unique_values']:
        fig_rel_freq_bar = px.bar(x=st.session_state['unique_values'], y=st.session_state['relative_frequencies'],
                                   labels={'x': 'Giá trị', 'y': 'Tần số tương đối (%)'})
        st.plotly_chart(fig_rel_freq_bar)
        fig_pie = px.pie(names=st.session_state['unique_values'], values=st.session_state['relative_frequencies'],
                         labels={'names': 'Giá trị', 'values': 'Tần số tương đối (%)'})
        st.plotly_chart(fig_pie)
    else:
        st.info("Vui lòng tính toán tần số ở tab 'Nhập liệu và Tạo bảng' trước.")