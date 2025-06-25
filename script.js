// 全局变量
let currentStudent = null;
const API_BASE_URL = 'http://localhost:5000/api';

// 工具函数
function showAlert(message, type = 'success') {
    const alertContainer = document.getElementById('alertContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.appendChild(alertDiv);
    
    // 自动移除
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

function showLoading() {
    document.getElementById('loading').style.display = 'block';
}

function hideLoading() {
    document.getElementById('loading').style.display = 'none';
}

async function apiCall(url, options = {}) {
    try {
        showLoading();
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        const data = await response.json();
        hideLoading();
        return data;
    } catch (error) {
        hideLoading();
        showAlert('网络错误: ' + error.message, 'danger');
        throw error;
    }
}

// 登录功能
document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const studentId = document.getElementById('studentId').value;
    const idCard = document.getElementById('idCard').value;
    const loginAlert = document.getElementById('loginAlert');
    
    try {
        const response = await apiCall(`${API_BASE_URL}/login`, {
            method: 'POST',
            body: JSON.stringify({
                stu_id: studentId,
                id_card: idCard,
                device_id: 'web'
            })
        });
        
        if (response.success) {
            currentStudent = response.student;
            showAlert('登录成功！');
            showMainInterface();
            loadInitialData();
        } else {
            loginAlert.textContent = response.message;
            loginAlert.style.display = 'block';
        }
    } catch (error) {
        loginAlert.textContent = '登录失败，请重试';
        loginAlert.style.display = 'block';
    }
});

function showMainInterface() {
    document.getElementById('loginSection').style.display = 'none';
    document.getElementById('mainSection').style.display = 'block';
    
    // 更新学生信息显示
    document.getElementById('studentName').textContent = currentStudent.name;
    document.getElementById('studentIdDisplay').textContent = currentStudent.stu_id;
    document.getElementById('studentDept').textContent = currentStudent.dept_id;
    
    // 控制管理员标签页的显示
    const adminTab = document.getElementById('admin-tab');
    if (currentStudent.isAdmin) {
        adminTab.style.display = 'block';
    } else {
        adminTab.style.display = 'none';
    }
}

function logout() {
    currentStudent = null;
    document.getElementById('mainSection').style.display = 'none';
    document.getElementById('loginSection').style.display = 'flex';
    document.getElementById('loginForm').reset();
    document.getElementById('loginAlert').style.display = 'none';
}

async function loadInitialData() {
    await Promise.all([
        loadCourses(),
        loadEnrolledCourses(),
        loadFriends(),
        loadMessages(),
        loadTransfers(),
        loadTables()
    ]);
}

// 选课功能
async function loadCourses() {
    try {
        const response = await apiCall(`${API_BASE_URL}/courses`);
        if (response.success) {
            const courseSelect = document.getElementById('courseSelect');
            courseSelect.innerHTML = '<option value="">请选择课程...</option>';
            
            response.courses.forEach(course => {
                const option = document.createElement('option');
                option.value = course.course_id;
                option.textContent = `${course.course_name} (${course.course_id}) - ${course.dept_name} - ${course.credit}学分`;
                courseSelect.appendChild(option);
            });
        }
    } catch (error) {
        showAlert('加载课程失败', 'danger');
    }
}

async function enrollCourse() {
    const courseId = document.getElementById('courseSelect').value;
    if (!courseId) {
        showAlert('请选择课程', 'warning');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE_URL}/enroll`, {
            method: 'POST',
            body: JSON.stringify({
                stu_id: currentStudent.stu_id,
                course_id: courseId
            })
        });
        
        if (response.success) {
            showAlert('选课成功！');
            loadEnrolledCourses();
            document.getElementById('courseSelect').value = '';
        } else {
            showAlert(response.message, 'danger');
        }
    } catch (error) {
        showAlert('选课失败', 'danger');
    }
}

async function loadEnrolledCourses() {
    try {
        const response = await apiCall(`${API_BASE_URL}/student/${currentStudent.stu_id}/courses`);
        if (response.success) {
            const container = document.getElementById('enrolledCourses');
            if (response.courses.length === 0) {
                container.innerHTML = '<p class="text-muted">暂无已选课程</p>';
                return;
            }
            
            let html = '<div class="table-responsive"><table class="table table-hover">';
            html += '<thead><tr><th>课程名称</th><th>课程号</th><th>院系</th><th>学分</th><th>成绩</th></tr></thead><tbody>';
            
            response.courses.forEach(course => {
                html += `<tr>
                    <td>${course.course_name}</td>
                    <td>${course.course_id}</td>
                    <td>${course.dept_name}</td>
                    <td>${course.credit}</td>
                    <td>${course.grade || '未录入'}</td>
                </tr>`;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        }
    } catch (error) {
        showAlert('加载已选课程失败', 'danger');
    }
}

// 好友功能
async function addFriend() {
    const friendId = document.getElementById('friendId').value;
    if (!friendId) {
        showAlert('请输入好友学号', 'warning');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE_URL}/friendship`, {
            method: 'POST',
            body: JSON.stringify({
                stu_id1: currentStudent.stu_id,
                stu_id2: friendId
            })
        });
        
        if (response.success) {
            showAlert('添加好友成功！');
            loadFriends();
            document.getElementById('friendId').value = '';
        } else {
            showAlert(response.message, 'danger');
        }
    } catch (error) {
        showAlert('添加好友失败', 'danger');
    }
}

async function loadFriends() {
    try {
        const response = await apiCall(`${API_BASE_URL}/student/${currentStudent.stu_id}/friends`);
        if (response.success) {
            const container = document.getElementById('friendsList');
            if (response.friends.length === 0) {
                container.innerHTML = '<p class="text-muted">暂无好友</p>';
                return;
            }
            
            let html = '<div class="table-responsive"><table class="table table-hover">';
            html += '<thead><tr><th>学号</th><th>姓名</th><th>院系</th></tr></thead><tbody>';
            
            response.friends.forEach(friend => {
                html += `<tr>
                    <td>${friend.stu_id}</td>
                    <td>${friend.name}</td>
                    <td>${friend.dept_name}</td>
                </tr>`;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        }
    } catch (error) {
        showAlert('加载好友列表失败', 'danger');
    }
}

async function getRecommendations() {
    try {
        const response = await apiCall(`${API_BASE_URL}/student/${currentStudent.stu_id}/recommendations`);
        if (response.success) {
            const container = document.getElementById('recommendations');
            if (response.recommendations.length === 0) {
                container.innerHTML = '<p class="text-muted">暂无推荐好友</p>';
                return;
            }
            
            let html = '<div class="list-group">';
            response.recommendations.forEach(rec => {
                html += `<div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-center">
                        <div>
                            <h6 class="mb-1">${rec.student.name} (${rec.student.stu_id})</h6>
                            <small class="text-muted">${rec.student.dept_name}</small>
                        </div>
                        <span class="badge bg-primary rounded-pill">${rec.common_friends} 个共同好友</span>
                    </div>
                </div>`;
            });
            html += '</div>';
            container.innerHTML = html;
        }
    } catch (error) {
        showAlert('获取推荐失败', 'danger');
    }
}

// 消息功能
async function sendMessage() {
    const toStu = document.getElementById('messageTo').value;
    const content = document.getElementById('messageContent').value;
    
    if (!toStu || !content) {
        showAlert('请填写完整信息', 'warning');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE_URL}/message`, {
            method: 'POST',
            body: JSON.stringify({
                from_stu_id: currentStudent.stu_id,
                to_stu_id: toStu,
                content: content,
                device_id: 'web'
            })
        });
        
        if (response.success) {
            showAlert('消息发送成功！');
            loadMessages();
            document.getElementById('messageTo').value = '';
            document.getElementById('messageContent').value = '';
        } else {
            showAlert(response.message, 'danger');
        }
    } catch (error) {
        showAlert('发送消息失败', 'danger');
    }
}

async function loadMessages() {
    try {
        const response = await apiCall(`${API_BASE_URL}/student/${currentStudent.stu_id}/messages`);
        if (response.success) {
            const container = document.getElementById('messagesList');
            if (response.messages.length === 0) {
                container.innerHTML = '<p class="text-muted">暂无消息</p>';
                return;
            }
            
            let html = '<div class="list-group">';
            response.messages.forEach(message => {
                const isFromMe = message.from_stu_id === currentStudent.stu_id;
                const otherName = isFromMe ? message.to_name : message.from_name;
                const otherId = isFromMe ? message.to_stu_id : message.from_stu_id;
                
                html += `<div class="list-group-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h6 class="mb-1">
                                ${isFromMe ? '发送给' : '来自'} ${otherName} (${otherId})
                            </h6>
                            <p class="mb-1">${message.content}</p>
                            <small class="text-muted">${new Date(message.send_time).toLocaleString()}</small>
                        </div>
                        <span class="badge ${isFromMe ? 'bg-primary' : 'bg-success'}">${isFromMe ? '发送' : '接收'}</span>
                    </div>
                </div>`;
            });
            html += '</div>';
            container.innerHTML = html;
        }
    } catch (error) {
        showAlert('加载消息失败', 'danger');
    }
}

// 转账功能
async function transferMoney() {
    const toStu = document.getElementById('transferTo').value;
    const amount = document.getElementById('transferAmount').value;
    
    if (!toStu || !amount) {
        showAlert('请填写完整信息', 'warning');
        return;
    }
    
    if (parseFloat(amount) <= 0) {
        showAlert('转账金额必须大于0', 'warning');
        return;
    }
    
    try {
        const response = await apiCall(`${API_BASE_URL}/transfer`, {
            method: 'POST',
            body: JSON.stringify({
                from_stu_id: currentStudent.stu_id,
                to_stu_id: toStu,
                amount: parseFloat(amount),
                device_id: 'web'
            })
        });
        
        if (response.success) {
            showAlert('转账成功！');
            loadTransfers();
            document.getElementById('transferTo').value = '';
            document.getElementById('transferAmount').value = '';
        } else {
            showAlert(response.message, 'danger');
        }
    } catch (error) {
        showAlert('转账失败', 'danger');
    }
}

async function loadTransfers() {
    try {
        const response = await apiCall(`${API_BASE_URL}/student/${currentStudent.stu_id}/transfers`);
        if (response.success) {
            const container = document.getElementById('transfersList');
            if (response.transfers.length === 0) {
                container.innerHTML = '<p class="text-muted">暂无转账记录</p>';
                return;
            }
            
            let html = '<div class="table-responsive"><table class="table table-hover">';
            html += '<thead><tr><th>类型</th><th>对方</th><th>金额</th><th>时间</th></tr></thead><tbody>';
            
            response.transfers.forEach(transfer => {
                const isFromMe = transfer.from_stu_id === currentStudent.stu_id;
                const otherName = isFromMe ? transfer.to_name : transfer.from_name;
                const otherId = isFromMe ? transfer.to_stu_id : transfer.from_stu_id;
                
                html += `<tr>
                    <td><span class="badge ${isFromMe ? 'bg-danger' : 'bg-success'}">${isFromMe ? '转出' : '转入'}</span></td>
                    <td>${otherName} (${otherId})</td>
                    <td class="${isFromMe ? 'text-danger' : 'text-success'}">${isFromMe ? '-' : '+'}￥${transfer.amount}</td>
                    <td>${new Date(transfer.transfer_time).toLocaleString()}</td>
                </tr>`;
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
        }
    } catch (error) {
        showAlert('加载转账记录失败', 'danger');
    }
}

// 管理员功能
let currentTableColumns = [];
let currentTableName = '';
let currentTableData = [];

async function loadTables() {
    if (!currentStudent?.isAdmin) return;
    
    try {
        const response = await apiCall(`${API_BASE_URL}/admin/tables?stu_id=${currentStudent.stu_id}`);
        if (response.success) {
            const tableSelect = document.getElementById('tableSelect');
            tableSelect.innerHTML = '<option value="">请选择表...</option>';
            
            response.tables.forEach(table => {
                const option = document.createElement('option');
                option.value = table;
                option.textContent = table;
                tableSelect.appendChild(option);
            });
            
            // 绑定表格选择事件
            tableSelect.addEventListener('change', loadTableData);
        }
    } catch (error) {
        showAlert('加载表格列表失败', 'danger');
    }
}

async function loadTableData() {
    if (!currentStudent?.isAdmin) return;
    
    const tableName = document.getElementById('tableSelect').value;
    if (!tableName) return;
    
    try {
        const response = await apiCall(`${API_BASE_URL}/admin/table/${tableName}?stu_id=${currentStudent.stu_id}`);
        if (response.success) {
            const container = document.getElementById('tableData');
            if (!response.data || response.data.length === 0) {
                container.innerHTML = '<p class="text-muted">暂无数据</p>';
                return;
            }
            
            // 创建表格
            let html = '<div class="table-responsive"><table class="table table-hover table-editable">';
            
            // 表头
            html += '<thead><tr>';
            Object.keys(response.data[0]).forEach(key => {
                html += `<th>${key}</th>`;
            });
            html += '<th>操作</th></tr></thead>';
            
            // 数据行
            html += '<tbody>';
            response.data.forEach(row => {
                html += '<tr>';
                Object.entries(row).forEach(([key, value]) => {
                    html += `<td data-field="${key}">${value}</td>`;
                });
                html += `<td>
                    <button class="btn btn-sm btn-danger delete-row">删除</button>
                </td>`;
                html += '</tr>';
            });
            
            html += '</tbody></table></div>';
            container.innerHTML = html;
            
            // 绑定编辑和删除事件
            bindAdminTableEvents();
        }
    } catch (error) {
        showAlert('加载表格数据失败', 'danger');
    }
}

function bindAdminTableEvents() {
    if (!currentStudent?.isAdmin) return;
    
    const table = document.querySelector('#tableData table');
    if (!table) return;
    
    // 单元格编辑
    table.addEventListener('dblclick', function(e) {
        if (e.target.tagName === 'TD' && e.target.dataset.field) {
            const originalValue = e.target.textContent;
            e.target.innerHTML = `<input type="text" class="form-control form-control-sm" value="${originalValue}">`;
            const input = e.target.querySelector('input');
            input.focus();
            
            input.addEventListener('blur', () => saveCellEdit(e.target, originalValue));
            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    saveCellEdit(e.target.parentNode, originalValue);
                }
            });
        }
    });
    
    // 删除行
    table.querySelectorAll('.delete-row').forEach(button => {
        button.addEventListener('click', async function() {
            if (!confirm('确定要删除这条记录吗？')) return;
            
            const row = this.closest('tr');
            const tableName = document.getElementById('tableSelect').value;
            const pkName = Object.keys(row.cells[0].dataset)[0];
            const pkValue = row.cells[0].textContent;
            
            try {
                const response = await apiCall(`${API_BASE_URL}/admin/table/${tableName}/${pkName}/${pkValue}?stu_id=${currentStudent.stu_id}`, {
                    method: 'DELETE'
                });
                
                if (response.success) {
                    row.remove();
                    showAlert('删除成功！');
                } else {
                    showAlert(response.message, 'danger');
                }
            } catch (error) {
                showAlert('删除失败', 'danger');
            }
        });
    });
}

async function saveCellEdit(cell, originalValue) {
    if (!currentStudent?.isAdmin) return;
    
    const input = cell.querySelector('input');
    if (!input) return;
    
    const newValue = input.value;
    if (newValue === originalValue) {
        cell.textContent = originalValue;
        return;
    }
    
    const row = cell.closest('tr');
    const tableName = document.getElementById('tableSelect').value;
    const pkName = Object.keys(row.cells[0].dataset)[0];
    const pkValue = row.cells[0].textContent;
    const fieldName = cell.dataset.field;
    
    try {
        const response = await apiCall(`${API_BASE_URL}/admin/table/${tableName}/${pkName}/${pkValue}?stu_id=${currentStudent.stu_id}`, {
            method: 'PUT',
            body: JSON.stringify({
                field: fieldName,
                value: newValue
            })
        });
        
        if (response.success) {
            cell.textContent = newValue;
            showAlert('更新成功！');
        } else {
            cell.textContent = originalValue;
            showAlert(response.message, 'danger');
        }
    } catch (error) {
        cell.textContent = originalValue;
        showAlert('更新失败', 'danger');
    }
}

// 新增按钮事件
const addRowBtn = document.getElementById('addRowBtn');
addRowBtn.onclick = function() {
    if (!currentTableColumns.length) {
        showAlert('请先加载表数据', 'warning');
        return;
    }
    const form = document.getElementById('addRowForm');
    form.innerHTML = '';
    currentTableColumns.forEach((col, idx) => {
        form.innerHTML += `<div class="mb-3"><label class="form-label">${col}</label><input type="text" class="form-control" name="${col}" ${idx===0?'placeholder="主键(可选)"':''}></div>`;
    });
    const modal = new bootstrap.Modal(document.getElementById('addRowModal'));
    modal.show();
}
// 新增表单提交
const addRowForm = document.getElementById('addRowForm');
const addRowSubmitBtn = document.getElementById('addRowSubmitBtn');
addRowForm.onsubmit = async function(e) {
    e.preventDefault();
    const formData = new FormData(addRowForm);
    const data = {};
    for (const [k, v] of formData.entries()) {
        if (v.trim() !== '') data[k] = v.trim();
    }
    const resp = await apiCall(`${API_BASE_URL}/admin/table/${currentTableName}`, {
        method: 'POST',
        body: JSON.stringify(data)
    });
    if (resp.success) {
        showAlert('新增成功');
        bootstrap.Modal.getInstance(document.getElementById('addRowModal')).hide();
        loadTableData();
    } else {
        showAlert(resp.message, 'danger');
    }
}

// 页面加载完成后的初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查是否有保存的登录状态
    const savedStudent = localStorage.getItem('currentStudent');
    if (savedStudent) {
        try {
            currentStudent = JSON.parse(savedStudent);
            showMainInterface();
            loadInitialData();
        } catch (error) {
            localStorage.removeItem('currentStudent');
        }
    }
});

// 保存登录状态
function saveLoginState() {
    if (currentStudent) {
        localStorage.setItem('currentStudent', JSON.stringify(currentStudent));
    }
}

// 清除登录状态
function clearLoginState() {
    localStorage.removeItem('currentStudent');
}

// 管理员消息全文检索
async function adminSearchMessage() {
    const keyword = document.getElementById('searchKeyword').value.trim();
    const fromStuId = document.getElementById('searchFromStuId').value.trim();
    if (!keyword) {
        showAlert('请输入关键词', 'warning');
        return;
    }
    let url = `${API_BASE_URL}/admin/search_message?stu_id=${currentStudent.stu_id}&keyword=${encodeURIComponent(keyword)}`;
    if (fromStuId) {
        url += `&from_stu_id=${encodeURIComponent(fromStuId)}`;
    }
    try {
        const resp = await apiCall(url);
        const container = document.getElementById('searchResults');
        if (resp.success && resp.results && resp.results.length > 0) {
            let html = '<div class="table-responsive"><table class="table table-hover">';
            html += '<thead><tr><th>消息ID</th><th>发信学号</th><th>内容</th></tr></thead><tbody>';
            resp.results.forEach(msg => {
                html += `<tr><td>${msg.message_id}</td><td>${msg.from_stu_id}</td><td>${msg.content}</td></tr>`;
            });
            html += '</tbody></table></div>';
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p class="text-muted">未找到相关消息</p>';
        }
    } catch (error) {
        showAlert('检索失败', 'danger');
    }
} 