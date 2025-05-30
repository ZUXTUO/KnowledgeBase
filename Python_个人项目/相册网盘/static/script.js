document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('uploadForm');
    const imageUploadInput = document.getElementById('imageUpload');

    const manageTagsButton = document.getElementById('manageTagsButton');
    const manageTagsModal = document.getElementById('manageTagsModal');
    const closeManageTagsModal = document.getElementById('closeManageTagsModal');
    const newTagInput = document.getElementById('newTagInput');
    const addNewTagButton = document.getElementById('addNewTagButton');
    const allTagsList = document.getElementById('allTagsList');
    const manageTagsMessage = document.getElementById('manageTagsMessage');

    const tagsContainer = document.getElementById('tagsContainer');
    const toggleTagsButton = document.getElementById('toggleTagsButton');

    const customConfirmDialog = document.getElementById('customConfirmDialog');
    const confirmMessage = document.getElementById('confirmMessage');
    const confirmYesButton = document.getElementById('confirmYes');
    const confirmNoButton = document.getElementById('confirmNo');

    let allAvailableTags = [];

    // Function to show custom confirm dialog
    function showCustomConfirm(message, onConfirm, onCancel) {
        confirmMessage.textContent = message;
        customConfirmDialog.classList.add('show');
        customConfirmDialog.style.display = 'flex';

        confirmYesButton.onclick = () => {
            customConfirmDialog.classList.remove('show');
            setTimeout(() => { customConfirmDialog.style.display = 'none'; }, 300);
            onConfirm();
        };

        confirmNoButton.onclick = () => {
            customConfirmDialog.classList.remove('show');
            setTimeout(() => { customConfirmDialog.style.display = 'none'; }, 300);
            if (onCancel) onCancel();
        };

        customConfirmDialog.onclick = (event) => {
            if (event.target === customConfirmDialog) {
                customConfirmDialog.classList.remove('show');
                setTimeout(() => { customConfirmDialog.style.display = 'none'; }, 300);
                if (onCancel) onCancel();
            }
        };
    }

    // Expose showCustomConfirm globally if needed by other scripts
    window.showCustomConfirm = showCustomConfirm;

    function showManageTagsMessage(message, isSuccess) {
        manageTagsMessage.textContent = message;
        manageTagsMessage.className = 'modal-message ' + (isSuccess ? 'success' : 'error');
        setTimeout(() => {
            manageTagsMessage.textContent = '';
            manageTagsMessage.className = 'modal-message';
        }, 3000);
    }

    function fetchAllTags() {
        return fetch('/api/all_tags')
            .then(response => response.json())
            .then(data => {
                allAvailableTags = data;
            })
            .catch(error => {
                console.error('获取所有标签失败:', error);
            });
    }

    fetchAllTags(); // Initial fetch for all tags

    if (uploadForm) {
        uploadForm.addEventListener('submit', function(event) {
            event.preventDefault();
            const formData = new FormData();
            if (imageUploadInput.files.length > 0) {
                formData.append('image', imageUploadInput.files[0]);

                fetch('/api/upload_image', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('图片上传成功！'); // Using alert for simplicity as per original, though modal is preferred
                        window.location.reload();
                    } else {
                        alert('图片上传失败: ' + (data.message || '未知错误'));
                    }
                })
                .catch(error => {
                    console.error('图片上传失败:', error);
                    alert('图片上传时发生错误。');
                });
            } else {
                alert('请选择一个图片文件。');
            }
        });
    }

    if (manageTagsButton) {
        manageTagsButton.addEventListener('click', function() {
            manageTagsModal.classList.add('show');
            manageTagsModal.style.display = 'flex';
            renderAllTags();
        });
    }

    if (closeManageTagsModal) {
        closeManageTagsModal.onclick = function() {
            manageTagsModal.classList.remove('show');
            setTimeout(() => {
                manageTagsModal.style.display = 'none';
            }, 300);
        }
    }

    function renderAllTags() {
        allTagsList.innerHTML = '';
        fetchAllTags().then(() => {
            allAvailableTags.forEach(tag => {
                const tagPill = document.createElement('div');
                tagPill.className = 'tag-pill';
                tagPill.textContent = tag.name;
                const deleteButton = document.createElement('span');
                deleteButton.className = 'remove-tag';
                deleteButton.textContent = 'x';
                deleteButton.onclick = () => {
                    showCustomConfirm(`确定要删除标签 "${tag.name}" 吗？这会从所有图片中移除该标签。`, () => {
                        deleteTag(tag.id);
                    });
                };
                tagPill.appendChild(deleteButton);
                allTagsList.appendChild(tagPill);
            });
        });
    }

    if (addNewTagButton) {
        addNewTagButton.addEventListener('click', function() {
            const tagName = newTagInput.value.trim();
            if (tagName) {
                fetch('/api/add_tag', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ tag_name: tagName })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showManageTagsMessage('标签添加成功！', true);
                        newTagInput.value = '';
                        renderAllTags();
                        fetchAllTags(); // Re-fetch all tags for suggestions
                    } else {
                        showManageTagsMessage('添加标签失败: ' + (data.message || '未知错误'), false);
                    }
                })
                .catch(error => {
                    console.error('添加标签失败:', error);
                    showManageTagsMessage('添加标签时发生错误。', false);
                });
            } else {
                showManageTagsMessage('标签名称不能为空。', false);
            }
        });
    }

    function deleteTag(tagId) {
        fetch(`/api/delete_tag/${tagId}`, {
            method: 'DELETE'
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showManageTagsMessage('标签删除成功。', true);
                renderAllTags();
                fetchAllTags(); // Re-fetch all tags for suggestions
                window.location.reload(); // Reload to reflect tag changes on gallery items
            } else {
                showManageTagsMessage('删除标签失败: ' + (data.message || '未知错误'), false);
            }
        })
        .catch(error => {
            console.error('删除标签失败:', error);
            showManageTagsMessage('删除标签时发生错误。', false);
        });
    }

    if (toggleTagsButton) {
        toggleTagsButton.addEventListener('click', function() {
            tagsContainer.classList.toggle('expanded');
            if (tagsContainer.classList.contains('expanded')) {
                toggleTagsButton.textContent = '收起标签';
            } else {
                toggleTagsButton.textContent = '展开标签';
            }
        });
    }
});
