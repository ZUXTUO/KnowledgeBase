document.addEventListener('DOMContentLoaded', function() {
    if (typeof currentImageId === 'undefined' || currentImageId === null) {
        return;
    }

    const detailImage = document.getElementById('detailImage');
    const detailFilename = document.getElementById('detailFilename');
    const detailRatingHiddenInput = document.getElementById('detailRating');
    const detailRatingStarsContainer = document.getElementById('detailRatingStars');
    const detailStars = document.querySelectorAll('#detailRatingStars .star');
    const detailTagsDisplay = document.getElementById('detailTagsDisplay');
    const editTagsButton = document.getElementById('editTagsButton');
    const deleteImageButton = document.getElementById('deleteImageButton');
    const detailMessage = document.getElementById('detailMessage');

    const editTagsModal = document.getElementById('editTagsModal');
    const closeEditTagsModal = editTagsModal.querySelector('.close-button');
    const modalTagInput = document.getElementById('modalTagInput');
    const modalSelectedTagsContainer = document.getElementById('modalSelectedTags');
    const modalTagSuggestions = document.getElementById('modalTagSuggestions');
    const editTagsMessage = document.getElementById('editTagsMessage');

    const imageViewerContainer = document.querySelector('.image-viewer-container');

    let allAvailableTags = [];
    let currentImageTags = new Set();

    let startX = 0;
    let endX = 0;
    const swipeThreshold = 50;

    function handleStart(e) {
        if (e.type === 'touchstart') {
            startX = e.touches[0].clientX;
        } else if (e.type === 'mousedown') {
            startX = e.clientX;
        }
    }

    function handleMove(e) {
        if (e.type === 'touchmove') {
            endX = e.touches[0].clientX;
        } else if (e.type === 'mousemove') {
            if (e.buttons === 1) {
                endX = e.clientX;
            }
        }
    }

    function handleEnd(e) {
        let diffX = endX - startX;

        if (startX === endX) {
            return;
        }

        if (Math.abs(diffX) > swipeThreshold) {
            if (diffX > 0) {
                if (prevImageId) {
                    window.location.href = `/image/${prevImageId}`;
                }
            } else {
                if (nextImageId) {
                    window.location.href = `/image/${nextImageId}`;
                }
            }
        }

        startX = 0;
        endX = 0;
    }

    if (imageViewerContainer) {
        imageViewerContainer.addEventListener('touchstart', handleStart, { passive: true });
        imageViewerContainer.addEventListener('touchmove', handleMove, { passive: true });
        imageViewerContainer.addEventListener('touchend', handleEnd);

        imageViewerContainer.addEventListener('mousedown', handleStart);
        imageViewerContainer.addEventListener('mousemove', handleMove);
        imageViewerContainer.addEventListener('mouseup', handleEnd);
        imageViewerContainer.addEventListener('mouseleave', handleEnd);
    }

    function showDetailMessage(message, isSuccess) {
        detailMessage.textContent = message;
        detailMessage.className = 'modal-message ' + (isSuccess ? 'success' : 'error');
        setTimeout(() => {
            detailMessage.textContent = '';
            detailMessage.className = 'modal-message';
        }, 3000);
    }

    function showEditTagsMessage(message, isSuccess) {
        editTagsMessage.textContent = message;
        editTagsMessage.className = 'modal-message ' + (isSuccess ? 'success' : 'error');
        setTimeout(() => {
            editTagsMessage.textContent = '';
            editTagsMessage.className = 'modal-message';
        }, 3000);
    }

    function renderStarRating(score) {
        detailStars.forEach((star, index) => {
            if (index < score) {
                star.classList.add('filled');
            } else {
                star.classList.remove('filled');
            }
        });
    }

    renderStarRating(parseInt(detailRatingHiddenInput.value));

    detailStars.forEach(star => {
        star.addEventListener('click', function() {
            const value = parseInt(this.dataset.value);
            renderStarRating(value);
            detailRatingHiddenInput.value = value;
            
            fetch(`/api/update_score/${currentImageId}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: `score=${encodeURIComponent(value)}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showDetailMessage('评分更新成功。', true);
                } else {
                    showDetailMessage('更新评分失败: ' + (data.message || '未知错误'), false);
                }
            })
            .catch(error => {
                console.error('保存评分错误:', error);
                showDetailMessage('保存评分时发生错误。', false);
            });
        });
    });

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

    function renderSelectedTagsInModal() {
        modalSelectedTagsContainer.innerHTML = '';
        currentImageTags.forEach(tag => {
            const tagPill = document.createElement('span');
            tagPill.className = 'tag-pill';
            tagPill.textContent = tag;
            const removeButton = document.createElement('span');
            removeButton.className = 'remove-tag';
            removeButton.textContent = 'x';
            removeButton.onclick = () => {
                currentImageTags.delete(tag);
                renderSelectedTagsInModal();
                updateTagsOnBackend();
            };
            tagPill.appendChild(removeButton);
            modalSelectedTagsContainer.appendChild(tagPill);
        });
    }

    function renderDetailTags(tagsString) {
        detailTagsDisplay.innerHTML = '';
        if (tagsString) {
            const tagsArray = tagsString.split(',').map(tag => tag.trim()).filter(tag => tag);
            tagsArray.forEach(tag => {
                const tagPill = document.createElement('span');
                tagPill.className = 'tag-pill';
                tagPill.textContent = tag;
                detailTagsDisplay.appendChild(tagPill);
            });
        } else {
            const noTagsSpan = document.createElement('span');
            noTagsSpan.className = 'no-tags';
            noTagsSpan.textContent = '无标签';
            detailTagsDisplay.appendChild(noTagsSpan);
        }
    }

    function updateTagsOnBackend() {
        const newTags = Array.from(currentImageTags).join(',');
        fetch(`/api/update_tags/${currentImageId}`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: `tags=${encodeURIComponent(newTags)}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showEditTagsMessage('标签更新成功。', true);
                renderDetailTags(data.new_tags_string);
            } else {
                showEditTagsMessage('更新标签失败: ' + (data.message || '未知错误'), false);
            }
        })
        .catch(error => {
            console.error('保存标签错误:', error);
            showEditTagsMessage('保存标签时发生错误。', false);
        });
    }

    if (editTagsButton) {
        editTagsButton.addEventListener('click', function() {
            currentImageTags.clear();
            const existingTags = detailTagsDisplay.querySelectorAll('.tag-pill');
            existingTags.forEach(pill => currentImageTags.add(pill.textContent));

            renderSelectedTagsInModal();
            fetchAllTags();
            editTagsModal.classList.add('show');
            editTagsModal.style.display = 'flex';
        });
    }

    if (closeEditTagsModal) {
        closeEditTagsModal.onclick = function() {
            editTagsModal.classList.remove('show');
            modalTagSuggestions.style.display = 'none';
            setTimeout(() => {
                editTagsModal.style.display = 'none';
            }, 300);
        }
    }

    window.onclick = function(event) {
        if (event.target == editTagsModal) {
            editTagsModal.classList.remove('show');
            modalTagSuggestions.style.display = 'none';
            setTimeout(() => {
                editTagsModal.style.display = 'none';
            }, 300);
        }
    }

    modalTagInput.addEventListener('input', function() {
        const inputText = this.value.toLowerCase();
        modalTagSuggestions.innerHTML = '';
        if (inputText.length > 0) {
            const filteredTags = allAvailableTags.filter(tag => 
                tag.name.toLowerCase().includes(inputText) && !currentImageTags.has(tag.name)
            );
            filteredTags.forEach(tag => {
                const suggestionItem = document.createElement('div');
                suggestionItem.className = 'tag-suggestion-item';
                suggestionItem.textContent = tag.name;
                suggestionItem.onclick = () => {
                    currentImageTags.add(tag.name);
                    renderSelectedTagsInModal();
                    modalTagInput.value = '';
                    modalTagSuggestions.style.display = 'none';
                    updateTagsOnBackend();
                };
                modalTagSuggestions.appendChild(suggestionItem);
            });
            modalTagSuggestions.style.display = filteredTags.length > 0 ? 'block' : 'none';
        } else {
            modalTagSuggestions.style.display = 'none';
        }
    });

    modalTagInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const newTag = this.value.trim();
            if (newTag && !currentImageTags.has(newTag)) {
                currentImageTags.add(newTag);
                renderSelectedTagsInModal();
                this.value = '';
                modalTagSuggestions.style.display = 'none';
                updateTagsOnBackend();
            }
        }
    });

    modalTagInput.addEventListener('blur', function() {
        setTimeout(() => {
            modalTagSuggestions.style.display = 'none';
        }, 100);
    });

    modalTagInput.addEventListener('focus', function() {
        const inputText = this.value.toLowerCase();
        modalTagSuggestions.innerHTML = '';
        const filteredTags = allAvailableTags.filter(tag => 
            tag.name.toLowerCase().includes(inputText) && !currentImageTags.has(tag.name)
        );
        modalTagSuggestions.style.display = filteredTags.length > 0 ? 'block' : 'none';
        filteredTags.forEach(tag => {
            const suggestionItem = document.createElement('div');
            suggestionItem.className = 'tag-suggestion-item';
            suggestionItem.textContent = tag.name;
            suggestionItem.onclick = () => {
                currentImageTags.add(tag.name);
                renderSelectedTagsInModal();
                modalTagInput.value = '';
                modalTagSuggestions.style.display = 'none';
                updateTagsOnBackend();
            };
            modalTagSuggestions.appendChild(suggestionItem);
        });
    });

    if (deleteImageButton) {
        deleteImageButton.onclick = function() {
            showCustomConfirm('确定要删除这张图片吗？此操作无法撤销。', () => {
                fetch(`/api/delete_image/${currentImageId}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        showDetailMessage('图片删除成功。', true);
                        window.location.href = '/'; 
                    } else {
                        showDetailMessage('删除图片失败: ' + (data.message || '未知错误'), false);
                    }
                })
                .catch(error => {
                    console.error('删除图片失败:', error);
                    showDetailMessage('删除图片时发生错误。', false);
                });
            });
        }
    }
});
