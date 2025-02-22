console.log("Chrome extension is so on")

user_location = {"Street": "214 PIERCE ST", "Apt_num": "311", "Zip": 47906, "City": "West Lafayette", "State": "IN"}

WAIT_TIME = 300

// Asssuming that user location is already filled

function auto_click_element(tagName) {
    try {
        // Find the first element with the specified tag
        const element = document.querySelector(tagName);

        if (element) {
            element.click(); // Simple direct click
            console.log('Successfully clicked element: ' + element);
            return true;
        } else {
            console.log(`No element found with tag: ${tagName}`);
            return false;
        }
    } catch (error) {
        console.error(`Error clicking element: ${error.message}`);
        return false;
    }
}

menu_button = '[data-quid="main-navigation-menu"]';
pizza_menu_button = '[data-quid="sub-navigation-pizza"]';
build_your_pizza_button = ".media__btn";
quantity_increment_button = '[data-quid="generic-quantity-increment"]';

small_pizza_button = '[data-quid="pizza-size-10-size"]';
medium_pizza_button = '[data-quid="pizza-size-12-size"]';
large_pizza_button = '[data-quid="pizza-size-14-size"]';

handTossed_button = '[data-quid="crust-input-14SCREEN"]';
crunchyThin_button = '[data-quid="crust-input-14THIN"]';
newYorkStyle_button = '[data-quid="crust-input-PBKIREZA"]';

add_to_order_button = '.single-page-pizza-builder__add-to-order';

popup_overlay_cheese = ".card--overlay";
yes_cheese_button = '[data-quid="builder-yes-step-upsell"]'

auto_click_element(menu_button);

function wait_for_loading_screen(next_button_tag) {
    return new Promise((resolve) => {
        loading_overlay_appeared_once = false;
        const interval = setInterval(() => {
            const loading_overlay = document.querySelector("#loadingOverlay");
            const next_button_to_click = document.querySelector(next_button_tag);

            if (next_button_to_click) {
                console.log("the next button appeared: " + next_button_to_click);
                clearInterval(interval);
                resolve(); // Continue execution
            }
            if (!loading_overlay) {
                if (loading_overlay_appeared_once) {
                    clearInterval(interval); // Stop checking
                    console.log("Loading screen disappeared!");
                    resolve(); // Continue execution
                }
            } else {
                loading_overlay_appeared_once = true;
            }
        }, WAIT_TIME);
    });
}

function pizza_builder_menu_exists() {
    return new Promise((resolve, reject) => {
        const startTime = Date.now();
        const timeout = 5000;  // 5 seconds timeout
        const checkElement = setInterval(() => {
            if (document.querySelector('[data-quid="modal-card-overlay-body"]')) {
                clearInterval(checkElement);
                resolve("Element found!");
            } else if (Date.now() - startTime > timeout) {
                clearInterval(checkElement);
                reject("Element not found within 5 seconds.");
            }
        }, 20);
    });
}

const orders = [
    {
        "quantity": 4,
        "size": "medium",
        "crust": "NEW YORK STYLE"
    },
    {
        "quantity": 15,
        "size": "small",
        "crust": "HAND TOSSED"
    },
    {
        "quantity": 3,
        "size": "large",
        "crust": "THIN CRUST"
    }
];

// Function where all the automated processing is taking place
// Processes individual order
async function start_ordering() {
    for (const order of orders) {
        await process_order(order);
        await new Promise(resolve => setTimeout(resolve, WAIT_TIME / 4));
    }
}

// Processes individual order
async function process_order(order) {
    // Goes on menu if we aren't on menu already
    if (!window.location.href.includes('/pages/order')) {
        auto_click_element(menu_button);
        await wait_for_loading_screen(pizza_menu_button);
    }

    auto_click_element(pizza_menu_button);
    await wait_for_loading_screen(build_your_pizza_button);

    auto_click_element(build_your_pizza_button);
    await pizza_builder_menu_exists();

    await make_pizza(order);
}

// Add size + crust
async function make_pizza(order) {
    // Handle quantity
    for (let i = 0; i < order.quantity - 1; i++) {
        auto_click_element(quantity_increment_button);
        await new Promise(resolve => setTimeout(resolve, WAIT_TIME / 4));
    }

    // Adding some wait time
    await new Promise(resolve => setTimeout(resolve, WAIT_TIME / 4));

    // Handle different sizes
    if (order.size == "small") {
        console.log("Selecting small size pizza");
        auto_click_element(small_pizza_button);
    } else if (order.size == "medium") {
        console.log("Selecting medium size pizza");
        auto_click_element(medium_pizza_button);
    } else if (order.size == "large") {
        console.log("Selecting large size pizza");
        auto_click_element(large_pizza_button);
    }

    // Adding some wait time
    await new Promise(resolve => setTimeout(resolve, WAIT_TIME / 4));

    // Handle different crusts
    if (order.crust == "HAND TOSSED") {
        console.log("Selecting hand tossed crust");
        auto_click_element(handTossed_button);
    } else if (order.crust == "THIN CRUST") {
        console.log("Selecting thin crust");
        auto_click_element(crunchyThin_button);
    } else if (order.crust == "NEW YORK STYLE") {
        console.log("Selecting New York style crust");
        auto_click_element(newYorkStyle_button);
    }

    await new Promise(resolve => setTimeout(resolve, WAIT_TIME / 4));

    auto_click_element(add_to_order_button);

    await new Promise(resolve => setTimeout(resolve, WAIT_TIME / 4));

    if (document.querySelector(popup_overlay_cheese)) {
        auto_click_element(yes_cheese_button);
    }

    await new Promise(resolve => setTimeout(resolve, WAIT_TIME / 4));
}

// Add functionality to -> Add multiple pizzas
// Add them with size, quantity, crust

function make_start_order_button() {
    let button = document.createElement('button');
    button.id = "start_order_button";
    button.textContent = "Start Order";
    button.style.position = "fixed";
    button.style.bottom = "20px";
    button.style.right = "20px";
    button.style.padding = "10px 15px";
    button.style.fontSize = "1em";
    button.style.borderRadius = "5px";
    button.style.backgroundColor = "#007bff";
    button.style.color = "white";
    button.style.border = "none";
    button.style.cursor = "pointer";

    button.addEventListener('click', async function() {
      await start_ordering();
    });

    document.body.appendChild(button);
}

make_start_order_button();

// Example usage:
// auto_click_element('button'); // Clicks the first button element
// auto_click_element('.submit-btn'); // Clicks element with class 'submit-btn'
// auto_click_element('#submit'); // Clicks element with ID 'submit'

const startTime = Date.now();