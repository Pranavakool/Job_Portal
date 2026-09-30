/**
 * JobPortal Interactive Frontend Scripts
 */
document.addEventListener('DOMContentLoaded', function () {
  // 1. Auto-dismiss alerts after 6 seconds
  const alerts = document.querySelectorAll('.alert-dismissible');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      try {
        const bsAlert = new bootstrap.Alert(alert);
        bsAlert.close();
      } catch (e) {
        alert.style.display = 'none';
      }
    }, 6000);
  });

  // 2. Client-side file validation for resume upload
  const resumeInput = document.querySelector('input[type="file"][name="resume"]');
  if (resumeInput) {
    resumeInput.addEventListener('change', function (e) {
      const file = this.files[0];
      if (!file) return;

      const allowedExtensions = ['pdf', 'doc', 'docx'];
      const fileExtension = file.name.split('.').pop().toLowerCase();
      const maxSize = 16 * 1024 * 1024; // 16 MB

      if (!allowedExtensions.includes(fileExtension)) {
        alert('Invalid file format! Please upload a PDF, DOC, or DOCX document.');
        this.value = '';
        return;
      }

      if (file.size > maxSize) {
        alert('File size exceeds the 16 MB limit. Please select a smaller file.');
        this.value = '';
        return;
      }
    });
  }

  // 3. Confirm Delete Modals or generic confirmation forms
  const confirmDeleteBtns = document.querySelectorAll('[data-confirm]');
  confirmDeleteBtns.forEach(function (btn) {
    btn.addEventListener('click', function (e) {
      const message = this.getAttribute('data-confirm') || 'Are you sure you want to proceed with this action?';
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });

  // 4. Initialize Bootstrap tooltips & popovers if present
  const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
  tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl);
  });
});
