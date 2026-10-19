function initLogSignal() {
    if (TLT.getState() === "destroyed") return;
    // --------------------------------------------------------------------------
    // ----------------------------------------------- Signal configuration -----
    // --------------------------------------------------------------------------
    const cfg = {
        errorLog: true,
        eventLog: false,
        signalsLog: true,
        fakeSignals: true,
        messageTypes: [
            // "all", // Verbose, use only during development
            "load",
            "click",
            "change",
            // "dlListener"
            // "ajaxListener"
        ],
        GAdataLayerName: "", // For GA typically "dataLayer". Do not include "window." in the name.
        GAeventsAllowList: [],
        signals: {
            loggedIn: {
                signal: {
                    signalType: "loggedIn",
                    // <<schema-start: loggedIn>>
                    loginMethod: null, // Text, Required
                    ssoProvider: null, // Text, Optional
                    mfaUsed: null, // Boolean, Optional
                    mfaMethod: null, // Text, Optional
                    // <<schema-end: loggedIn>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: { // Objet, Optional
                    },
                    consent: { // Objet, Optional
                    },
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {
                }
            },
            accountRegistered: {
                signal: {
                    signalType: "accountRegistered",
                    // <<schema-start: accountRegistered>>
                    registrationMethod: null, // Text, Required
                    ssoProvider: null, // Text, Optional
                    registrationSource: null, // Text, Optional
                    mfaEnabled: null, // Boolean, Optional
                    // <<schema-end: accountRegistered>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {
                }
            },
            pageView: {
                signal: {
                    signalType: "pageView",
                    // <<schema-start: pageView>>
                    url: null, // Text, Required
                    pageCategory: null, // Text, Optional
                    pageGroup: null, // Text, Optional
                    // <<schema-end: pageView>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {
                }
            },
            onSiteSearch: {
                signal: {
                    signalType: "onSiteSearch",
                    // <<schema-start: onSiteSearch>>
                    searchTerm: null, // Text, Required
                    numberOfResults: null, // Number, Required
                    // <<schema-end: onSiteSearch>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {
                }
            },
            productView: {
                signal: {
                    signalType: "productView",
                    // <<schema-start: productView>>
                    productId: null, // Text, Required
                    productName: null, // Text, Required
                    availability: null, // Text, Optional
                    brandName: null, // Text, Optional
                    brandDescription: null, // Text, Optional
                    model: null, // Text, Optional
                    msrp: null, // Number, Optional
                    sku: null, // Text, Optional
                    productStatus: null, // Text, Optional
                    productRating: null, // Number, Optional
                    dateAdded: null, // Date, Optional
                    tags: [], // Array, Optional
                    categories: null, // Text, Optional
                    currency: null, // Text, Optional
                    productDescription: null, // Text, Optional
                    inventoryQuantity: null, // Number, Optional
                    unitPrice: null, // Number, Optional
                    discount: null, // Number, Optional
                    productCategory: null, // Text, Optional
                    productUrls: [], // Array, Optional
                    imageUrls: [], // Array, Optional
                    shoppingCartUrl: null, // Text, Optional
                    virtualCategory: null, // Text, Optional
                    actionState: null, // Text, Optional
                    resumedCartItem: null, // Text, Optional
                    promotionId: null, // Text, Optional
                    productCategoryId: null, // Text, Optional
                    // <<schema-end: productView>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {}
            },
            productConfiguration: {
                signal: {
                    signalType: "productConfiguration",
                    // <<schema-start: productConfiguration>>
                    productId: null, // Text, Required
                    productName: null, // Text, Required
                    configurationType: null, // Text, Optional
                    currency: null, // Text, Optional
                    productDescription: null, // Text, Optional
                    inventoryQuantity: null, // Number, Optional
                    unitPrice: null, // Number, Optional
                    discount: null, // Number, Optional
                    productCategory: null, // Text, Optional
                    productUrls: [], // Array, Optional
                    imageUrls: [], // Array, Optional
                    shoppingCartUrl: null, // Text, Optional
                    virtualCategory: null, // Text, Optional
                    actionState: null, // Text, Optional
                    resumedCartItem: null, // Text, Optional
                    promotionId: null, // Text, Optional
                    productCategoryId: null, // Text, Optional
                    // <<schema-end: productConfiguration>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {}
            },
            // Include removedFromCart within addToCart logic
            addToCart: {
                signal: {
                    signalType: "addToCart",
                    // <<schema-start: addToCart>>
                    productId: null, // Text, Required
                    productName: null, // Text, Required
                    itemQuantity: null, // Number, Required
                    unitPrice: null, // Number, Required
                    currency: null, // Text, Optional
                    productDescription: null, // Text, Optional
                    discount: null, // Number, Optional
                    productCategory: null, // Text, Optional
                    productUrls: [], // Array, Optional
                    imageUrls: [], // Array, Optional
                    shoppingCartUrl: null, // Text, Optional
                    virtualCategory: null, // Text, Optional
                    actionState: null, // Text, Optional
                    resumedCartItem: null, // Text, Optional
                    promotionId: null, // Text, Optional
                    productCategoryId: null, // Text, Optional
                    // <<schema-end: addToCart>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {}
            },
            order: {
                signal: {
                    signalType: "order",
                    // <<schema-start: order>>
                    orderId: null, // Text, Required
                    orderedItems: [], // Array, Required
                    orderSubtotal: null, // Number, Optional
                    orderShippingHandling: null, // Number, Optional
                    orderTax: null, // Number, Optional
                    orderDiscount: null, // Number, Optional
                    orderValue: null, // Number, Optional
                    currency: null, // Text, Optional
                    // <<schema-end: order>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                // <<schema-items-start: order>>
                // orderedItem properties:
                //   productId: "", // Text, Required
                //   productName: "", // Text, Required
                //   productDescription: "", // Text, Optional
                //   itemQuantity: 0, // Number, Optional
                //   unitPrice: 0, // Number, Required
                //   discount: 0, // Number, Optional
                //   productCategory: "", // Text, Optional
                //   productUrls: [], // Array, Optional
                //   imageUrls: [], // Array, Optional
                //   shoppingCartUrl: "", // Text, Optional
                //   virtualCategory: "", // Text, Optional
                //   actionState: "", // Text, Optional
                //   resumedCartItem: "", // Text, Optional
                //   promotionId: "", // Text, Optional
                //   productCategoryId: "" // Text, Optional
                // <<schema-items-end: order>>
                triggers: [],
                enhance: function (signal, help) {}
            },
            error: {
                signal: {
                    signalType: "error",
                    // <<schema-start: error>>
                    errorType: null, // Enum ("USER"|"APPLICATION"), Required
                    errorText: null, // Text, Required
                    errorIdentifier: null, // Text, Optional
                    // <<schema-end: error>>
                    effect: "negative", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {}
            },
            richMediaInteraction: {
                signal: {
                    signalType: "richMediaInteraction",
                    // <<schema-start: richMediaInteraction>>
                    mediaId: null, // Text, Required
                    url: null, // Text, Optional
                    mediaCategory: null, // Text, Optional
                    mediaName: null, // Text, Optional
                    interactionType: null, // Enum ("LOAD"|"LAUNCH"|"PAUSE"|"CONTINUE"|"COMPLETE"|"STOP"|"ENLARGE"), Optional
                    // <<schema-end: richMediaInteraction>>
                    effect: "positive", // Enum ("negative"|"positive"), Required
                    audience: {}, // Object, Optional
                    consent: {}, // Object, Optional
                    signalCustomAttributes: [] // Object, Optional
                },
                triggers: [],
                enhance: function (signal, help) {}
            }
        }
    };

    // --------------------------------------------------------------------------
    // ----------------------------------------- logSignal helper functions -----
    // --------------------------------------------------------------------------

    function warn(clog, e) {
        if (clog && console && cfg.errorLog) {
            console.warn("Acoustic Connect: Warning! \u{1F6A8}");
            console.warn(clog);
            if (e) console.warn(e);
        }
    }

    const requiredFields = {
        loggedIn: ["loginMethod"],
        accountRegistered: ["registrationMethod"],
        pageView: ["url"],
        onSiteSearch: ["searchTerm", "numberOfResults"],
        productView: ["productId", "productName"],
        productConfiguration: ["productId", "productName"],
        addToCart: [
            "productId",
            "productName",
            "itemQuantity",
            "unitPrice"
        ],
        removedFromCart: [
            "productId",
            "productName",
            "itemQuantity",
            "unitPrice"
        ],
        order: ["orderId", "orderedItems"],
        error: ["errorType", "errorText"],
        richMediaInteraction: ["mediaId"],
    };
    const requiredOrderedItemFields = [
        "productId",
        "productName",
        "unitPrice"
    ];
    function validateSignal(signal) {
        function isEmpty(v) {
            return v === null || v === undefined || v === ""
                || (Array.isArray(v) && v.length === 0)
                || (typeof v === "object" && !Array.isArray(v) && Object.keys(v).length === 0);
        }
        function getMissing(obj, fields) {
            return fields.filter(function (f) {
                return isEmpty(obj[f]);
            });
        }
        function stripEmptyOptional(obj, required) {
            Object.keys(obj).forEach(function (key) {
                if (key === "signalType" || required.indexOf(key) !== -1) return;
                if (isEmpty(obj[key])) delete obj[key];
            });
        }
        const required = requiredFields[signal.signalType] || [];
        const missing = getMissing(signal, required);
        if (missing.length) {
            warn("Signal '" + signal.signalType + "' is missing required field(s): " + missing.join(", ") + ". Signal not sent.");
            return false;
        }
        if (signal.signalType === "order") {
            for (let idx = 0; idx < signal.orderedItems.length; idx++) {
                const missingItem = getMissing(signal.orderedItems[idx], requiredOrderedItemFields);
                if (missingItem.length) {
                    warn("Signal 'order' orderedItems[" + idx + "] is missing required field(s): " + missingItem.join(", ") + ". Signal not sent.");
                    return false;
                }
                stripEmptyOptional(signal.orderedItems[idx], requiredOrderedItemFields);
            }
        }
        stripEmptyOptional(signal, required);
        return signal;
    }

    function log(signal, clog) {
        let bufferStr;
        let newBuffer;
        let bufferObj;
        if (!validateSignal(signal)) return;
        signal.name = signal.signalType + " generated by website";
        signal.category = "Behavior";
        if (TLT.isInitialized()) {
            if (cfg.fakeSignals === true) {
                window.TLT.logCustomEvent("logSignal", { description: "Fake logSignal Message", signal: signal });
            } else {
                window.TLT.logSignal(signal);
            }
            return;
        }
        if (!TLT.isInitialized() && sessionStorage) {
            warn("TLT is not initialized! Buffering signal until next time TLT initializes.");
            bufferStr = sessionStorage.getItem("aco-buffer");
            if (!bufferStr) {
                newBuffer = [{ signal: signal, clog: clog }];
                sessionStorage.setItem("aco-buffer", JSON.stringify(newBuffer));
            } else {
                bufferObj = JSON.parse(bufferStr);
                bufferObj.push({ signal: signal, clog: clog });
                sessionStorage.setItem("aco-buffer", JSON.stringify(bufferObj));
            }
        }
    }

    function getNodeFromXpath(query, scope = document) {
        const xpath = JSON.parse(query);

        let elem = scope;
        let pathElem;
        let pathElemIsHost;
        let x;
        let j;
        let k;
        let len;
        let jlen;

        if (!query || !xpath) return null;

        for (x = 0, len = xpath.length; x < len && elem; x += 1) {
            pathElem = xpath[x];
            pathElemIsHost = pathElem.length > 1 && pathElem[pathElem.length - 1] === "h";
            if (pathElem.length === 1 || (pathElem.length === 2 && pathElemIsHost)) {
                if (scope.getElementById) {
                    elem = scope.getElementById(pathElem[0]);
                } else if (scope.querySelector) {
                    elem = scope.querySelector("#" + pathElem[0]);
                } else {
                    elem = null;
                }
            } else {
                for (j = 0, k = -1, jlen = elem.childNodes.length; j < jlen; j += 1) {
                    if (elem.childNodes[j].nodeType === 1 && TLT.utils.getTagName(elem.childNodes[j]) === pathElem[0].toLowerCase()) {
                        k += 1;
                        if (k === pathElem[1]) {
                            elem = elem.childNodes[j];
                            break;
                        }
                    }
                }
                if (k !== pathElem[1]) return null;
            }

            if (!elem) return null;
        }

        return (elem === scope || !elem) ? null : elem;
    }

    function parsePath(pathStr) {
        const keys = [];
        const re = /\[(['"])((?:(?!\1).)*)\1\]|([^.[\]]+)/g;
        let m = re.exec(pathStr);
        while (m !== null) {
            keys.push(m[2] !== undefined ? m[2] : m[3]);
            m = re.exec(pathStr);
        }
        return keys;
    }

    function getAttribute(dotStr, webEvent) {
        try {
            const value = parsePath(dotStr).reduce((o, n) => o[n], webEvent);
            return value;
        } catch {
            return undefined;
        }
    }

    function matchEvent(attributes, webEvent) {
        const keysArr = Object.keys(attributes);
        for (let k = 0; k < keysArr.length; k++) {
            const dotStr = keysArr[k];
            const attrVal = getAttribute(dotStr, webEvent);
            if (typeof attributes[dotStr] === "string") {
                if (attributes[dotStr] !== attrVal) return false;
            }
            if (typeof attributes[dotStr] === "object" && attributes[dotStr] instanceof RegExp) {
                if (!attributes[dotStr].test(attrVal)) return false;
            }
        }
        return true;
    }

    function store(key, value) {
        const storeKey = cfg.sessionStorageKey || "aco-store";

        if (!sessionStorage) {
            warn("Session storage unavailable");
            return false;
        }

        let acoStore = sessionStorage.getItem(storeKey) || "{}";
        acoStore = JSON.parse(acoStore);
        if (typeof key === "object" && key.signalType && value === undefined) {
            if (acoStore[key.signalType]) {
                acoStore[key.signalType].push(key);
            } else {
                acoStore[key.signalType] = [key];
            }
        }
        if (key && value !== undefined) {
            acoStore[key] = value;
        }
        sessionStorage.setItem(storeKey, JSON.stringify(acoStore));
        return true;
    }

    function retrieve(key, del) {
        const storeKey = cfg.sessionStorageKey || "aco-store";

        if (!sessionStorage) {
            warn("Session storage unavailable");
            return false;
        }

        let acoStore = sessionStorage.getItem(storeKey) || "{}";
        acoStore = JSON.parse(acoStore);
        const value = acoStore[key] || "";
        if (del && del === "delete") {
            delete acoStore[key];
            if (Object.keys(acoStore).length === 0) {
                sessionStorage.removeItem(storeKey);
            } else {
                sessionStorage.setItem(storeKey, JSON.stringify(acoStore));
            }
        }
        return value;
    }

    function cssGet(selector, attr, flag, root = document) {
        let num;
        if (root) {
            if (root.shadowRoot) {
                root = root.shadowRoot;
            }
            const element = root.querySelector(selector);
            if (element) {
                if (!attr) {
                    return element;
                }
                if (element[attr]) {
                    if (flag === "n" || flag === "ne") {
                        if (flag === "n") {
                            num = element[attr].replace(/[^0-9. ]+/g, "");
                        }
                        if (flag === "ne") {
                            num = element[attr].replace(/[^0-9, ]+/g, "").replace(",", ".");
                        }
                        num = Number(num.trim().split(" ")[0]);
                        return num || null;
                    }
                    return String(element[attr]).trim() || null;
                }
            }
        }
        return null;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    function validateEmailFormat(email) {
        return emailRegex.test(email);
    }

    function stripHtml(html) {
        if (!html || typeof html !== "string") return "";
        return html
            .replace(/<[^>]*>/g, "")
            .replace(/\s+/g, " ")
            .trim();
    }

    function getQueryParam(str, param, n) {
        let value;
        try {
            const url = new URL(str);
            value = url.searchParams.get(param);
        } catch {
            const params = new URLSearchParams(str);
            value = params.get(param);
        }
        if (n === "n") {
            return Number(value) || null;
        }
        return value ? decodeURIComponent(value) : null;
    }

    function logEnhanced(thisSig, thisWebEvent, thisDlEvent, thisLabel, thisDelay) {
        function delayLogEnhanced() {
            const help = {
                webEvent: thisWebEvent,
                dlEvent: thisDlEvent,
                cssGet: cssGet,
                label: thisLabel,
                log: log,
                store: store,
                retrieve: retrieve,
                getNodeFromXpath: getNodeFromXpath,
                validateEmailFormat: validateEmailFormat,
                stripHtml: stripHtml,
                getQueryParam: getQueryParam
            };
            let thisSignal;
            try {
                thisSignal = thisSig.enhance(thisSig.signal, help);
                if (thisSignal && thisSignal.signalType) {
                    log(thisSignal, thisSignal.signalType + " signal");
                }
            } catch (e) {
                const sigDisplayType = thisSig.signal?.signalType || "utility";
                warn("Error enhancing " + sigDisplayType + " signal:\n" + JSON.stringify(thisSig, undefined, 2), e);
            }
        }
        window.setTimeout(delayLogEnhanced, thisDelay);
    }

    (function () {
        const bufferStr = sessionStorage.getItem("aco-buffer");
        let bufferObj;
        let b;
        let signal;
        let clog;
        if (bufferStr) {
            bufferObj = JSON.parse(bufferStr);
            for (b = 0; b < bufferObj.length; b++) {
                signal = bufferObj[b].signal;
                clog = bufferObj[b].clog;
                log(signal, clog);
            }
            warn(bufferObj.length + " signal(s) sent from buffer");
            sessionStorage.removeItem("aco-buffer");
        }
    }());

    const sigArr = Object.keys(cfg.signals);
    function msgHandler(msg) {
        let dlEvent;
        let sig;
        if (cfg.eventLog) {
            console.log("%cAcoustic Connect: Type " + msg.type + " message \u{1F441}%c\n" + JSON.stringify(msg, undefined, 2), "font-weight: bold", "");
        }
        try {
            for (let s = 0; s < sigArr.length; s++) {
                sig = cfg.signals[sigArr[s]];
                if (sig.triggers && sig.triggers.length) {
                    for (let i = 0; i < sig.triggers.length; i++) {
                        const label = sig.triggers[i].label || "";
                        const delay = sig.triggers[i].delay || 0;
                        if (matchEvent(sig.triggers[i].attributes, msg)) {
                            if (sig.enhance) {
                                if (msg.type === 5 && msg.customEvent.name === "dataLayerPush") {
                                    dlEvent = msg.customEvent.data.dlEvent;
                                }
                                logEnhanced(sig, msg, dlEvent, label, delay);
                            } else {
                                log(sig.signal, sig.signal.signalType + " signal");
                            }
                        }
                    }
                }
            }
        } catch (e) {
            warn("error evaluating " + sig.signal.signalType + " signal", e);
        }
    }

    TLT.registerBridgeCallbacks([{
        enabled: true,
        cbType: "messageRedirect",
        cbFunction: (function () {
            let lastCount = 0;
            return function (msg, msgObj) {
                if (msgObj && msgObj.count > lastCount) {
                    lastCount = msgObj.count;

                       // New EndSignal for tealeaf Eventing
                        if (msgObj.type === 21) {
                            const wrapped = [
                                { customSignal: msgObj.signal },
                                { endSignal: true }
                            ]
                            TLT.logCustomEvent("customSignal", wrapped);
                    }

                    if (cfg.signalsLog && msgObj.type === 21) {
                        console.log("%cAcoustic Connect: Type 21 " + msgObj.signal.signalType + " signal \u{1F3AF}%c\n" + JSON.stringify(msgObj.signal, undefined, 2), "font-weight: bold", "");
                        return msgObj;
                    }
                    if (cfg.signalsLog && cfg.fakeSignals && msgObj.type === 5 && msgObj?.customEvent?.name === "logSignal") {
                        console.log("%cAcoustic Connect: Type 5 fake " + msgObj.customEvent.data.signal.signalType + " signal \u{1F978}%c\n" + JSON.stringify(msgObj.customEvent.data.signal, undefined, 2), "font-weight: bold", "");
                        return msgObj;
                    }
                    if (cfg.messageTypes.includes("all")
                                    || (cfg.messageTypes.includes("load") && msgObj.type === 2 && msgObj.screenview.type === "LOAD")
                                    || (cfg.messageTypes.includes("click") && msgObj.type === 4 && msgObj.event.type === "click")
                                    || (cfg.messageTypes.includes("change") && msgObj.type === 4 && msgObj.event.type === "change")
                                    || (cfg.messageTypes.includes("mousedown") && msgObj.type === 4 && msgObj.event.type === "mousedown")
                                    || (cfg.messageTypes.includes("dlListener") && msgObj.type === 5 && msgObj.customEvent.name === "dlListener")
                                    || (cfg.messageTypes.includes("ajaxListener") && msgObj.type === 5 && msgObj.customEvent.name === "ajaxListener")
                    ) {
                        msgHandler(msgObj);
                    }
                    if (msgObj.type === 5 && msgObj.customEvent.name === "dlListener") return null;
                }
                return msgObj;
            };
        }())
    }]);

    (function () {
        if (!cfg.messageTypes.includes("dlListener")) return;
        if ((TLT.getCoreConfig().modules.dataLayer && TLT.getCoreConfig().modules.dataLayer.enabled !== false)
                    || !cfg.GAdataLayerName
                    || !cfg.GAeventsAllowList.length) {
            warn("Invalid dlListener configuration");
            return;
        }

        if (!window[cfg.GAdataLayerName]) {
            warn("No dataLayer found");
            return;
        }
        if (!Array.isArray(window[cfg.GAdataLayerName])
                    || typeof window[cfg.GAdataLayerName].push !== "function") {
            warn("window." + cfg.GAdataLayerName + " exists but is not a standard dataLayer");
            return;
        }
        if (window[cfg.GAdataLayerName].__istrackingPush) {
            warn("dataLayer push is already patched");
            return;
        }
        if (!window.__tempDataLayer) {
            window.__tempDataLayer = [...window[cfg.GAdataLayerName]];
        }

        const originalPush = window[cfg.GAdataLayerName].push;

        function dlListener(arg) {
            try {
                if (arg.event && (cfg.GAeventsAllowList.includes(arg.event) || cfg.GAeventsAllowList.includes("all"))) {
                    TLT.logCustomEvent("dlListener", arg);
                }
            } catch (e) {
                warn("Error sending dlListener message: " + e.message);
            }
        }

        try {
            Object.defineProperty(window[cfg.GAdataLayerName], "push", {
                value: function (...args) {
                    args.forEach((arg) => dlListener(arg));
                    return originalPush.apply(this, args);
                },
                writable: true,
                configurable: true
            });
            window[cfg.GAdataLayerName].__istrackingPush = true;

        } catch (e) {
            warn("Error monkey patching dataLayer.push: " + e.message);
            window[cfg.GAdataLayerName] = originalPush;
        }

        try {
            if (window[cfg.GAdataLayerName].__istrackingPush && window.__tempDataLayer && window.__tempDataLayer.length) {
                window.__tempDataLayer.forEach((oldEvent) => {
                    if (oldEvent?.event) {
                        if (cfg.GAeventsAllowList.includes(oldEvent.event) || cfg.GAeventsAllowList.includes("all")) {
                            TLT.logCustomEvent("dlListener", oldEvent);
                        }
                    }
                });
                delete window.__tempDataLayer;
            }
        } catch (e) {
            warn("Error processing temporary dataLayer: " + e.message);
        }
    }());
}
