 
 function togglePassword(inputId, eyeOpenId, eyeClosedId) {
    const passwordInput = document.getElementById(inputId);
    const eyeOpen = document.getElementById(eyeOpenId);
    const eyeClosed = document.getElementById(eyeClosedId);

    if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        eyeOpen.classList.add('hidden');
        eyeClosed.classList.remove('hidden');
    } else {
        passwordInput.type = 'password';
        eyeOpen.classList.remove('hidden');
        eyeClosed.classList.add('hidden');
    }
}



let isMining = true;
let currentProgress = 73;

// Buy Modal Functions
function openBuyModal(method) {
    const modal = document.getElementById('buyModal');
    const paymentDiv = document.getElementById('paymentMethod');
    
    let paymentContent = '';
    switch(method) {
        case 'mpesa':
            paymentContent = `
                <div class="flex items-center">
                    <div class="w-8 h-8 bg-green-500 rounded mr-3 flex items-center justify-center">
                        <span class="text-xs font-bold text-white">M</span>
                    </div>
                    <span>M-Pesa</span>
                </div>
                <div class="mt-3">
                    <input type="tel" placeholder="Phone Number" class="w-full p-2 bg-white/10 border border-white/20 rounded text-white placeholder-gray-400">
                </div>
            `;
            break;
        case 'paypal':
            paymentContent = `
                <div class="flex items-center">
                    <div class="w-8 h-8 bg-blue-500 rounded mr-3 flex items-center justify-center">
                        <span class="text-xs font-bold text-white">P</span>
                    </div>
                    <span>PayPal</span>
                </div>
                <p class="text-sm text-gray-400 mt-2">You'll be redirected to PayPal to complete payment</p>
            `;
            break;
        case 'card':
            paymentContent = `
                <div class="flex items-center mb-3">
                    <div class="w-8 h-8 bg-purple-500 rounded mr-3 flex items-center justify-center">
                        <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z"></path>
                        </svg>
                    </div>
                    <span>Credit/Debit Card</span>
                </div>
                <div class="space-y-2">
                    <input type="text" placeholder="Card Number" class="w-full p-2 bg-white/10 border border-white/20 rounded text-white placeholder-gray-400">
                    <div class="flex space-x-2">
                        <input type="text" placeholder="MM/YY" class="flex-1 p-2 bg-white/10 border border-white/20 rounded text-white placeholder-gray-400">
                        <input type="text" placeholder="CVV" class="flex-1 p-2 bg-white/10 border border-white/20 rounded text-white placeholder-gray-400">
                    </div>
                </div>
            `;
            break;
    }
    
    paymentDiv.innerHTML = paymentContent;
    modal.classList.remove('hidden');
}

function closeBuyModal() {
    document.getElementById('buyModal').classList.add('hidden');
}

function openSendModal() {
    document.getElementById('sendModal').classList.remove('hidden');
    // document.body.style.overflow = 'hidden';
}

function closeSendModal() {
    document.getElementById('sendModal').classList.add('hidden');
    // document.body.style.overflow = '';
}

function openAddWalletModal() {
    document.getElementById('addWalletModal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden'; 
}

function closeAddWalletModal() {
    document.getElementById('addWalletModal').classList.add('hidden');
    document.body.style.overflow = '';
    document.body.style.overflow = ''; 
}

// Update KENA amount based on USD input
document.addEventListener('DOMContentLoaded', function() {
    const buyAmountInput = document.getElementById('buyAmount');
    if (buyAmountInput) {
        buyAmountInput.addEventListener('input', function() {
            const usdAmount = parseFloat(this.value) || 0;
            const kenaAmount = (usdAmount / 0.30).toFixed(2); // $0.30 per KENA
            document.getElementById('kenaAmount').textContent = kenaAmount;
        });
    }
});

function processPurchase() {
    const amount = document.getElementById('buyAmount').value;
    if (!amount || amount <= 0) {
        alert('Please enter a valid amount');
        return;
    }
    
    // Simulate purchase process
    alert('Purchase initiated! You will receive a confirmation shortly.');
    closeBuyModal();
    
    // Add to transaction history
    setTimeout(() => {
        addTransaction('purchase', parseFloat(amount) / 0.30, 'Purchase via payment method');
    }, 2000);
}

function sendTransaction() {
    const address = document.getElementById('recipientAddress').value;
    const amount = document.getElementById('sendAmount').value;
    
    if (!address || !amount || amount <= 0) {
        alert('Please fill in all required fields');
        return;
    }
    
    if (parseFloat(amount) > 12547.82) {
        alert('Insufficient balance');
        return;
    }
    
    // Simulate transaction
    alert('Transaction sent! It will be confirmed shortly.');
    closeSendModal();
    
    // Add to transaction history
    setTimeout(() => {
        addTransaction('sent', -parseFloat(amount), `To: ${address.substring(0, 10)}...`);
    }, 1000);
}

function addTransaction(type, amount, details) {
    const transactionsList = document.getElementById('transactionsList');
    const isPositive = amount > 0;
    const icon = type === 'purchase' ? 'M12 6v6m0 0v6m0-6h6m-6 0H6' : 
                type === 'sent' ? 'M20 12H4' : 'M12 6v6m0 0v6m0-6h6m-6 0H6';
    const iconColor = isPositive ? 'green' : 'red';
    
    const newTransaction = document.createElement('div');
    newTransaction.className = 'flex items-center justify-between p-4 bg-white/5 rounded-lg border border-white/5 opacity-0';
    newTransaction.innerHTML = `
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-${iconColor}-500/20 rounded-full flex items-center justify-center">
                <svg class="w-5 h-5 text-${iconColor}-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${icon}"></path>
                </svg>
            </div>
            <div>
                <p class="font-semibold">${type.charAt(0).toUpperCase() + type.slice(1)}</p>
                <p class="text-sm text-gray-400">${details}</p>
                <p class="text-xs text-gray-500">Just now</p>
            </div>
        </div>
        <div class="text-right">
            <p class="text-${iconColor}-400 font-semibold">${isPositive ? '+' : ''}${Math.abs(amount).toFixed(2)} KENA</p>
            <p class="text-sm text-gray-400">≈ ${(Math.abs(amount) * 0.30).toFixed(2)}</p>
        </div>
    `;
    
    transactionsList.insertBefore(newTransaction, transactionsList.firstChild);
    
    // Animate in
    setTimeout(() => {
        newTransaction.style.opacity = '1';
        newTransaction.style.transition = 'opacity 0.5s ease-in-out';
    }, 100);
    
    // Remove oldest if more than 5 transactions
    if (transactionsList.children.length > 5) {
        transactionsList.removeChild(transactionsList.lastChild);
    }
}

// Mining Functions
function toggleMining() {
    const button = document.getElementById('miningToggle');
    const status = document.getElementById('miningStatus');
    
    isMining = !isMining;
    
    if (isMining) {
        button.textContent = 'Stop Mining';
        button.className = 'w-full p-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white rounded-lg hover:from-green-600 hover:to-emerald-700 transition-all font-semibold';
        status.textContent = 'Active';
        status.className = 'text-green-400 font-semibold';
        startMiningAnimation();
    } else {
        button.textContent = 'Start Mining';
        button.className = 'w-full p-3 bg-gradient-to-r from-red-500 to-red-600 text-white rounded-lg hover:from-red-600 hover:to-red-700 transition-all font-semibold';
        status.textContent = 'Inactive';
        status.className = 'text-red-400 font-semibold';
    }
}

function startMiningAnimation() {
    if (!isMining) return;
    
    const progressElement = document.getElementById('blockProgress');
    const progressBar = document.getElementById('progressBar');
    const hashRateElement = document.getElementById('hashRate');
    const sharesElement = document.getElementById('shares');
    
    // Update progress
    currentProgress += Math.random() * 2;
    if (currentProgress >= 100) {
        currentProgress = 0;
        // Add mining reward transaction
        addTransaction('mining', 12.5, 'Block reward');
        // Update shares
        const currentShares = parseInt(sharesElement.textContent.replace(',', ''));
        sharesElement.textContent = (currentShares + 1).toLocaleString();
    }
    
    progressElement.textContent = Math.floor(currentProgress) + '%';
    progressBar.style.width = Math.floor(currentProgress) + '%';
    
    // Simulate hash rate fluctuation
    const baseHashRate = 245.7;
    const fluctuation = (Math.random() - 0.5) * 20;
    hashRateElement.textContent = (baseHashRate + fluctuation).toFixed(1) + ' MH/s';
    
    // Continue animation
    setTimeout(startMiningAnimation, 2000);
}

// Real-time updates
function updateDashboard() {
    // Simulate price changes
    const priceElements = document.querySelectorAll('.text-2xl.font-bold');
    if (Math.random() > 0.95) { // 5% chance of price update
        // Update wallet balances slightly
        priceElements.forEach(el => {
            if (el.textContent.includes(',')) {
                const current = parseFloat(el.textContent.replace(',', ''));
                const change = (Math.random() - 0.5) * 10;
                el.textContent = (current + change).toLocaleString('en-US', {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }
        });
    }
}

// Start mining animation if mining is active
if (isMining) {
    startMiningAnimation();
}

// Update dashboard every 10 seconds
setInterval(updateDashboard, 10000);

// Add hover effects to cards
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.bg-white\\/5, .bg-gradient-to-br');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            if (!this.classList.contains('transform')) {
                this.style.transform = 'translateY(-2px)';
                this.style.transition = 'transform 0.3s ease';
            }
        });
        card.addEventListener('mouseleave', function() {
            if (!this.classList.contains('transform')) {
                this.style.transform = 'translateY(0)';
            }
        });
    });
});



document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('userMenuButton');
    const menu = document.getElementById('userMenu');
    const arrow = document.getElementById('dropdownArrow');
    
    let isOpen = false;
    
    // Toggle dropdown
    function toggleDropdown() {
        isOpen = !isOpen;
        
        if (isOpen) {
            menu.classList.remove('opacity-0', 'invisible', 'scale-95');
            menu.classList.add('opacity-100', 'visible', 'scale-100');
            arrow.classList.add('rotate-180');
            button.setAttribute('aria-expanded', 'true');
        } else {
            menu.classList.remove('opacity-100', 'visible', 'scale-100');
            menu.classList.add('opacity-0', 'invisible', 'scale-95');
            arrow.classList.remove('rotate-180');
            button.setAttribute('aria-expanded', 'false');
        }
    }
    
    // Close dropdown
    function closeDropdown() {
        if (isOpen) {
            toggleDropdown();
        }
    }
    
    // Button click handler
    button.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleDropdown();
    });
    
    // Click outside to close
    document.addEventListener('click', function(e) {
        if (!document.getElementById('userDropdown').contains(e.target)) {
            closeDropdown();
        }
    });
    
    // Escape key to close
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeDropdown();
        }
    });
    
    // Prevent menu clicks from closing dropdown
    menu.addEventListener('click', function(e) {
        // Only prevent if it's not a link or form submission
        if (!e.target.closest('a') && !e.target.closest('button[type="submit"]')) {
            e.stopPropagation();
        }
    });
});

// make transaction dropdown functional
document.addEventListener('DOMContentLoaded', function() {
    const selectButton = document.getElementById('walletSelectButton');
    const dropdownMenu = document.getElementById('walletDropdownMenu');
    const selectArrow = document.getElementById('walletSelectArrow');
    const selectedWalletName = document.getElementById('selectedWalletName');
    const selectedWalletBalance = document.getElementById('selectedWalletBalance');
    const walletError = document.getElementById('walletError');
    
    // Find the hidden select element - Django auto-generates ID as "id_FIELDNAME"
    const hiddenSelect = document.querySelector('#sendKenaForm select[name="wallet"]');
    
    if (!hiddenSelect) {
        console.error('Wallet select field not found!');
        return;
    }
    
    let isOpen = false;
    
    // Toggle dropdown
    if (selectButton) {
        selectButton.addEventListener('click', function(e) {
            e.stopPropagation();
            isOpen = !isOpen;
            
            if (isOpen) {
                dropdownMenu.classList.remove('hidden');
                dropdownMenu.classList.add('show');
                selectArrow.style.transform = 'rotate(180deg)';
            } else {
                dropdownMenu.classList.add('hidden');
                dropdownMenu.classList.remove('show');
                selectArrow.style.transform = 'rotate(0deg)';
            }
        });
    }
    
    // Handle wallet selection
    const walletOptions = document.querySelectorAll('.wallet-option');
    walletOptions.forEach(option => {
        option.addEventListener('click', function() {
            const walletId = this.dataset.walletId;
            const walletName = this.dataset.walletName;
            const walletBalance = this.dataset.walletBalance;
            const walletType = this.dataset.walletType;
            
            // Update hidden select
            hiddenSelect.value = walletId;
            
            // Update display
            selectedWalletName.textContent = walletName;
            selectedWalletBalance.textContent = `${parseFloat(walletBalance).toFixed(2)} KENA • ${walletType}`;
            
            // Clear error
            if (walletError) {
                walletError.classList.add('hidden');
            }
            
            // Close dropdown
            dropdownMenu.classList.add('hidden');
            dropdownMenu.classList.remove('show');
            selectArrow.style.transform = 'rotate(0deg)';
            isOpen = false;
            
            // Remove selection styling from all options
            walletOptions.forEach(opt => {
                opt.classList.remove('bg-white/10');
            });
            
            // Add selection styling
            this.classList.add('bg-white/10');
        });
    });
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (selectButton && dropdownMenu) {
            if (!selectButton.contains(e.target) && !dropdownMenu.contains(e.target)) {
                dropdownMenu.classList.add('hidden');
                dropdownMenu.classList.remove('show');
                selectArrow.style.transform = 'rotate(0deg)';
                isOpen = false;
            }
        }
    });
    
    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isOpen) {
            dropdownMenu.classList.add('hidden');
            dropdownMenu.classList.remove('show');
            selectArrow.style.transform = 'rotate(0deg)';
            isOpen = false;
        }
    });
});

document.getElementById('sendKenaForm').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    const sendButton = document.getElementById('sendButton');
    const messageContainer = document.getElementById('sendMessageContainer');
    const url = document.getElementById('dashboardUrl').value;
    
    // Disable button and show loading
    sendButton.disabled = true;
    sendButton.textContent = 'Processing...';
    messageContainer.classList.add('hidden');
    
    fetch(url, {
        method: 'POST',
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            messageContainer.innerHTML = `
                <div class="p-4 bg-green-500/20 border border-green-500 rounded-lg text-green-400">
                    ${data.message}
                </div>
            `;
            messageContainer.classList.remove('hidden');
            
            // Reset form and close modal after 2 seconds
            setTimeout(() => {
                closeSendModal();
                location.reload(); // Refresh to update balances
            }, 2000);
        } else {
            let errorHtml = '<div class="p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-400"><ul class="list-disc list-inside">';
            
            if (data.error) {
                errorHtml += `<li>${data.error}</li>`;
            }
            
            if (data.errors) {
                for (const [field, errors] of Object.entries(data.errors)) {
                    errors.forEach(error => {
                        errorHtml += `<li>${error}</li>`;
                    });
                }
            }
            
            errorHtml += '</ul></div>';
            messageContainer.innerHTML = errorHtml;
            messageContainer.classList.remove('hidden');
        }
    })
    .catch(error => {
        messageContainer.innerHTML = `
            <div class="p-4 bg-red-500/20 border border-red-500 rounded-lg text-red-400">
                An error occurred. Please try again.
            </div>
        `;
        messageContainer.classList.remove('hidden');
    })
    .finally(() => {
        sendButton.disabled = false;
        sendButton.textContent = 'Send Transaction';
    });
});