import SwiftUI

@main
struct Eco_CartApp: App {
    @State private var showLanding = true
    @StateObject var cartManager = CartManager() // ✅ Create only once here

    var body: some Scene {
        WindowGroup {
            if showLanding {
                LandingView(showLanding: $showLanding)
                    .environmentObject(cartManager) // ✅ Pass to all views
            } else {
                MainTabView()
                    .environmentObject(cartManager) // ✅ Pass to all views
            }
        }
    }
}
