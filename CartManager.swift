import SwiftUI

class CartManager: ObservableObject {
    @Published var cartItems: [EcoCartItem] = []

    func addToCart(item: EcoCartItem) {
        if !cartItems.contains(where: { $0.name == item.name }) {
            cartItems.append(item)
        }
    }

    func removeFromCart(item: EcoCartItem) {
        cartItems.removeAll { $0.id == item.id }
    }
}

struct EcoCartItem: Identifiable, Equatable {
    let id = UUID()
    let name: String
    let imageName: String
    let description: String
    let score: Double
}
