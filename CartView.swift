import SwiftUI

struct CartView: View {
    @EnvironmentObject var cartManager: CartManager

    var body: some View {
        NavigationView {
            ZStack {
                LinearGradient(
                    gradient: Gradient(colors: [Color("Cream"), Color("LeafGreen")]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                if cartManager.cartItems.isEmpty {
                    VStack(spacing: 16) {
                        Text("Your cart is empty")
                            .font(.title2)
                            .fontWeight(.medium)

                        NavigationLink(destination: DashboardView()) {
                            Text("Search Items")
                                .fontWeight(.semibold)
                                .padding(.vertical, 12)
                                .padding(.horizontal, 28)
                                .background(Color("EarthBrown"))
                                .foregroundColor(.white)
                                .clipShape(Capsule())
                        }
                    }
                } else {
                    VStack {
                        ScrollView {
                            LazyVStack(spacing: 16) {
                                ForEach(cartManager.cartItems) { item in
                                    HStack(spacing: 16) {
                                        Image(item.imageName)
                                            .resizable()
                                            .scaledToFill()
                                            .frame(width: 60, height: 60)
                                            .clipShape(RoundedRectangle(cornerRadius: 12))
                                            .shadow(radius: 2)

                                        VStack(alignment: .leading, spacing: 4) {
                                            Text(item.name)
                                                .font(.headline)

                                            Text(item.description)
                                                .font(.caption)
                                                .foregroundColor(.gray)

                                            Text(String(format: "Score: %.1f", item.score * 10))
                                                .font(.caption2)
                                                .foregroundColor(.secondary)
                                        }

                                        Spacer()

                                        // 🗑️ Trash Button
                                        Button(action: {
                                            cartManager.removeFromCart(item: item)
                                        }) {
                                            Image(systemName: "trash")
                                                .foregroundColor(.red)
                                        }
                                    }
                                    .padding()
                                    .background(Color.white)
                                    .cornerRadius(16)
                                    .shadow(color: Color.black.opacity(0.05), radius: 4, x: 0, y: 2)
                                    .padding(.horizontal)
                                }
                            }
                            .padding(.top)
                        }

                        VStack(spacing: 8) {
                            Text("Overall Score:")
                                .font(.subheadline)
                                .foregroundColor(.secondary)

                            Text(String(format: "%.1f / 10", averageScore()))
                                .font(.system(size: 32, weight: .bold, design: .rounded))
                                .foregroundColor(Color("EarthBrown"))
                        }
                        .padding()
                        .frame(maxWidth: .infinity)
                        .background(Color.white)
                        .cornerRadius(16)
                        .shadow(color: Color.black.opacity(0.1), radius: 6, x: 0, y: 4)
                        .padding(.horizontal)
                        .padding(.bottom, 16)
                    }
                }
            }
            .navigationTitle("Cart")
        }
    }

    func averageScore() -> Double {
        let total = cartManager.cartItems.reduce(0) { $0 + $1.score }
        return cartManager.cartItems.isEmpty ? 0.0 : total / Double(cartManager.cartItems.count) * 10
    }
}
