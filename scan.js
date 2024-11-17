// // Global variables
// let stream = null;
// let videoElement = null;
// let captureCanvas = null;

// // Initialize the application
// document.addEventListener('DOMContentLoaded', () => {
//     initializeElements();
//     setupEventListeners();
// });

// function initializeElements() {
//     // Create video element for camera feed
//     videoElement = document.createElement('video');
//     videoElement.setAttribute('autoplay', '');
//     videoElement.setAttribute('playsinline', '');
    
//     // Create canvas for capturing images
//     captureCanvas = document.createElement('canvas');
// }

// function setupEventListeners() {
//     // Find all scan cards
//     const scanCard = document.querySelector('.card[onclick="startScan(false)"]');
//     const scanAndAddCard = document.querySelector('.card[onclick="startScan(true)"]');
    
//     // Remove the inline onclick attributes and add event listeners
//     if (scanCard) {
//         scanCard.removeAttribute('onclick');
//         scanCard.addEventListener('click', () => startScan(false));
//     }
    
//     if (scanAndAddCard) {
//         scanAndAddCard.removeAttribute('onclick');
//         scanAndAddCard.addEventListener('click', () => startScan(true));
//     }
// }

// async function startScan(isRegistration) {
//     try {
//         // Create and show camera modal
//         const modal = createCameraModal();
//         document.body.appendChild(modal);
        
//         // Start camera
//         stream = await navigator.mediaDevices.getUserMedia({ 
//             video: { facingMode: 'user' }
//         });
        
//         videoElement.srcObject = stream;
//         const cameraContainer = modal.querySelector('.camera-container');
//         cameraContainer.appendChild(videoElement);
        
//         // Set up capture button with isRegistration parameter
//         const captureBtn = modal.querySelector('.capture-btn');
//         captureBtn.onclick = () => captureImage(isRegistration);
        
//         // Set up close button
//         const closeBtn = modal.querySelector('.close-btn');
//         closeBtn.onclick = closeCamera;
        
//     } catch (error) {
//         showError('Failed to access camera: ' + error.message);
//     }
// }

// function createCameraModal() {
//     const modal = document.createElement('div');
//     modal.className = 'camera-modal';
//     modal.innerHTML = `
//         <div class="modal-content">
//             <div class="camera-container"></div>
//             <div class="button-container">
//                 <button class="capture-btn">Capture</button>
//                 <button class="close-btn">Close</button>
//             </div>
//         </div>
//     `;
//     return modal;
// }

// function closeCamera() {
//     if (stream) {
//         stream.getTracks().forEach(track => track.stop());
//     }
//     const modal = document.querySelector('.camera-modal');
//     if (modal) {
//         modal.remove();
//     }
// }

// async function captureImage(isRegistration) {
//     try {
//         // Set canvas dimensions to match video
//         captureCanvas.width = videoElement.videoWidth;
//         captureCanvas.height = videoElement.videoHeight;
        
//         // Draw video frame to canvas
//         const context = captureCanvas.getContext('2d');
//         context.drawImage(videoElement, 0, 0);
        
//         // Get base64 image data
//         const imageData = captureCanvas.toDataURL('image/jpeg');
        
//         if (isRegistration) {
//             showRegistrationModal(imageData);
//         } else {
//             await scanFace(imageData);
//         }
        
//     } catch (error) {
//         showError('Failed to capture image: ' + error.message);
//     }
// }

// async function scanFace(imageData) {
//     try {
//         const response = await fetch('http://localhost:5000/api/scan', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({ image: imageData })
//         });
        
//         const data = await response.json();
        
//         if (response.ok) {
//             showStudentInfo(data);
//             closeCamera();
//         } else {
//             showError(data.error);
//         }
        
//     } catch (error) {
//         showError('Failed to process scan: ' + error.message);
//     }
// }

// function showRegistrationModal(imageData) {
//     const modal = document.createElement('div');
//     modal.className = 'registration-modal';
//     modal.innerHTML = `
//         <div class="modal-content">
//             <h2 class="text-2xl font-bold mb-4">Student Registration</h2>
//             <form id="registration-form">
//                 <div class="form-group">
//                     <label for="studentId">Student ID:</label>
//                     <input type="text" id="studentId" required>
//                 </div>
//                 <div class="form-group">
//                     <label for="firstName">First Name:</label>
//                     <input type="text" id="firstName" required>
//                 </div>
//                 <div class="form-group">
//                     <label for="lastName">Last Name:</label>
//                     <input type="text" id="lastName" required>
//                 </div>
//                 <div class="button-container">
//                     <button type="submit">Save</button>
//                     <button type="button" class="cancel-btn">Cancel</button>
//                 </div>
//             </form>
//         </div>
//     `;
    
//     document.body.appendChild(modal);
    
//     // Set up form submission
//     const form = modal.querySelector('#registration-form');
//     form.onsubmit = (e) => handleRegistration(e, imageData);
    
//     // Set up cancel button
//     modal.querySelector('.cancel-btn').onclick = () => {
//         modal.remove();
//         closeCamera();
//     };
// }

// async function handleRegistration(event, imageData) {
//     event.preventDefault();
    
//     const formData = {
//         studentId: document.getElementById('studentId').value,
//         firstName: document.getElementById('firstName').value,
//         lastName: document.getElementById('lastName').value,
//         image: imageData
//     };
    
//     try {
//         const response = await fetch('http://localhost:5000/api/register', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify(formData)
//         });
        
//         const data = await response.json();
        
//         if (response.ok) {
//             showSuccess('Student registered successfully');
//             document.querySelector('.registration-modal').remove();
//             closeCamera();
//         } else {
//             showError(data.error);
//         }
        
//     } catch (error) {
//         showError('Failed to register student: ' + error.message);
//     }
// }

// function showStudentInfo(data) {
//     const infoBox = document.getElementById('student-info-box');
//     const infoContent = document.getElementById('student-info-content');
    
//     infoContent.innerHTML = `
//         <p><strong>Student ID:</strong> ${data.student_id}</p>
//         <p><strong>Name:</strong> ${data.first_name} ${data.last_name}</p>
//         <p><strong>Scan Time:</strong> ${data.scan_time}</p>
//     `;
    
//     infoBox.style.display = 'block';
    
//     // Hide info after 5 seconds
//     setTimeout(() => {
//         infoBox.style.display = 'none';
//     }, 5000);
// }

// function showError(message) {
//     const errorDiv = document.createElement('div');
//     errorDiv.className = 'error-message';
//     errorDiv.textContent = message;
//     document.body.appendChild(errorDiv);
    
//     setTimeout(() => errorDiv.remove(), 3000);
// }

// function showSuccess(message) {
//     const successDiv = document.createElement('div');
//     successDiv.className = 'success-message';
//     successDiv.textContent = message;
//     document.body.appendChild(successDiv);
    
//     setTimeout(() => successDiv.remove(), 3000);
// }