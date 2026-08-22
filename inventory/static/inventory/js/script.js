/* JavaScript for Medical Inventory System */

document.addEventListener("DOMContentLoaded", function () {
    // Sidebar toggle logic for mobile/desktop
    const menuToggle = document.getElementById("menu-toggle");
    const sidebarWrapper = document.getElementById("sidebar-wrapper");

    if (menuToggle && sidebarWrapper) {
        menuToggle.addEventListener("click", function (e) {
            e.preventDefault();
            sidebarWrapper.classList.toggle("toggled");
        });
    }

    // Auto-dismiss alert banners after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Dynamic Calculation for Purchase Form
    const purchaseMedSelect = document.getElementById("id_purchase_medicine");
    const purchaseQtyInput = document.getElementById("id_purchase_qty");
    const purchasePriceInput = document.getElementById("id_purchase_price");
    const purchaseTotalDisplay = document.getElementById("purchase_total_display");

    function updatePurchaseTotal() {
        const qty = parseFloat(purchaseQtyInput ? purchaseQtyInput.value : 0) || 0;
        const price = parseFloat(purchasePriceInput ? purchasePriceInput.value : 0) || 0;
        const total = qty * price;
        if (purchaseTotalDisplay) {
            purchaseTotalDisplay.innerText = "₹" + total.toFixed(2);
        }
    }

    if (purchaseQtyInput) purchaseQtyInput.addEventListener("input", updatePurchaseTotal);
    if (purchasePriceInput) purchasePriceInput.addEventListener("input", updatePurchaseTotal);

    // Auto-fill price and supplier when medicine is selected in Purchase Form
    if (purchaseMedSelect) {
        purchaseMedSelect.addEventListener("change", function () {
            const medId = this.value;
            if (medId) {
                fetch(`/api/medicines/${medId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (purchasePriceInput && data.purchase_price) {
                            purchasePriceInput.value = data.purchase_price;
                        }
                        const supplierSelect = document.getElementById("id_supplier");
                        if (supplierSelect && data.supplier_id) {
                            supplierSelect.value = data.supplier_id;
                        }
                        updatePurchaseTotal();
                    })
                    .catch(err => console.error("Error fetching medicine detail:", err));
            }
        });
    }

    // Dynamic Calculation & Stock Auto-fill for Sale Form
    const saleMedSelect = document.getElementById("id_sale_medicine");
    const saleQtyInput = document.getElementById("id_sale_qty");
    const salePriceInput = document.getElementById("id_sale_price");
    const saleTotalDisplay = document.getElementById("sale_total_display");
    const availableStockDisplay = document.getElementById("available_stock_display");

    function updateSaleTotal() {
        const qty = parseFloat(saleQtyInput ? saleQtyInput.value : 0) || 0;
        const price = parseFloat(salePriceInput ? salePriceInput.value : 0) || 0;
        const total = qty * price;
        if (saleTotalDisplay) {
            saleTotalDisplay.innerText = "₹" + total.toFixed(2);
        }
    }

    if (saleQtyInput) saleQtyInput.addEventListener("input", updateSaleTotal);
    if (salePriceInput) salePriceInput.addEventListener("input", updateSaleTotal);

    if (saleMedSelect) {
        saleMedSelect.addEventListener("change", function () {
            const medId = this.value;
            if (medId) {
                fetch(`/api/medicines/${medId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (salePriceInput && data.selling_price) {
                            salePriceInput.value = data.selling_price;
                        }
                        if (availableStockDisplay && data.quantity !== undefined) {
                            availableStockDisplay.innerText = data.quantity + " units available";
                            if (data.quantity === 0) {
                                availableStockDisplay.className = "form-text text-danger font-monospace fw-bold";
                            } else {
                                availableStockDisplay.className = "form-text text-success font-monospace fw-bold";
                            }
                        }
                        updateSaleTotal();
                    })
                    .catch(err => console.error("Error fetching medicine detail:", err));
            }
        });
    }
});
