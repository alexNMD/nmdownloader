class MagicFocus {

    constructor(parent) {
        this.parent = parent;

        if (!this.parent) return;

        this.focus = document.createElement('div');
        this.focus.classList.add('magic-focus');
        this.parent.classList.add('has-magic-focus');
        this.parent.appendChild(this.focus);

        const inputs = this.parent.querySelectorAll('input, textarea, select');

        for (let input of inputs) {
            input.addEventListener('focus', () => {
                window.magicFocus.show();
            });

            input.addEventListener('blur', () => {
                window.magicFocus.hide();
            });
        }
    }

    show() {
        const el = document.activeElement;

        if (!['INPUT', 'SELECT', 'TEXTAREA'].includes(el.nodeName)) {
            return;
        }

        clearTimeout(this.reset);

        let targetEl = el;

        if (['checkbox', 'radio'].includes(el.type)) {
            const label = document.querySelector(`[for="${el.id}"]`);
            if (label) {
                targetEl = label;
            }
        }

        this.focus.style.top = `${targetEl.offsetTop || 0}px`;
        this.focus.style.left = `${targetEl.offsetLeft || 0}px`;
        this.focus.style.width = `${targetEl.offsetWidth || 0}px`;
        this.focus.style.height = `${targetEl.offsetHeight || 0}px`;
    }

    hide() {
        const el = document.activeElement;

        if (!['INPUT', 'SELECT', 'TEXTAREA', 'LABEL'].includes(el.nodeName)) {
            this.focus.style.width = '0';
        }

        this.reset = setTimeout(() => {
            window.magicFocus.focus.removeAttribute('style');
        }, 200);
    }
}

// Initialize
window.magicFocus = new MagicFocus(document.querySelector('.form'));

let lastChecked = null;
const radioInputs = document.querySelectorAll('input[name="option"]');

radioInputs.forEach(input => {
    input.addEventListener('click', function(e) {
        if (this === lastChecked) {
            this.checked = false;
            lastChecked = null;
            window.magicFocus.focus.removeAttribute('style');
        } else {
            lastChecked = this;
        }
    });
});
