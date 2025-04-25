import SwiftUI

struct ProductDetailView: View {
    let productName: String
    let imageName: String

    @EnvironmentObject var cartManager: CartManager
    @State private var isAdded = false

    let score: Double = 8.1
    let components: [String: Double] = [
        "Total Carbon": 0.32,
        "Packaging": 0.21,
        "Transportation": 0.12
    ]
    let rationale: String = """
    • This product uses minimal packaging materials.\n
    • Transportation emissions are low due to local sourcing.\n
    • Overall carbon footprint is significantly below average.
    """

    var body: some View {
        GeometryReader { geometry in
            ZStack(alignment: .bottom) {
                LinearGradient(
                    gradient: Gradient(colors: [Color("Cream"), Color("LeafGreen")]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                ScrollView {
                    VStack(spacing: 20) {
                        Image(imageName)
                            .resizable()
                            .scaledToFit()
                            .frame(height: 240)
                            .clipShape(RoundedRectangle(cornerRadius: 20))
                            .padding(.top, 40)

                        VStack(alignment: .leading, spacing: 16) {
                            HStack {
                                Text(productName)
                                    .font(.title2)
                                    .fontWeight(.bold)

                                Spacer()

                                Text(String(format: "%.1f / 10", score))
                                    .font(.title)
                                    .fontWeight(.bold)
                                    .foregroundColor(Color("EarthBrown"))
                            }

                            Divider()

                            VStack(alignment: .leading, spacing: 6) {
                                Text("Score Breakdown:")
                                    .font(.headline)

                                ForEach(components.sorted(by: { $0.key < $1.key }), id: \.key) { key, value in
                                    HStack {
                                        Text(key + ":")
                                        Spacer()
                                        Text(String(format: "%.2f", value))
                                    }
                                    .font(.subheadline)
                                }
                            }

                            Divider()

                            VStack(alignment: .leading, spacing: 6) {
                                Text("Why this score?")
                                    .font(.headline)
                                Text(rationale)
                                    .font(.body)
                                    .foregroundColor(.gray)
                            }
                        }
                        .padding()
                        .background(Color.white)
                        .cornerRadius(20)
                        .shadow(radius: 5)
                        .padding(.horizontal)
                        .padding(.bottom, 100)
                    }
                }

                // ✅ Button: Add or Tick Mark
                Button(action: {
                    if !isAdded {
                        let item = EcoCartItem(
                            name: productName,
                            imageName: imageName,
                            description: "Description goes here",
                            score: score / 10
                        )
                        cartManager.addToCart(item: item)
                        isAdded = true
                    }
                }) {
                    HStack {
                        if isAdded {
                            Image(systemName: "checkmark.circle.fill")
                                .font(.title2)
                        } else {
                            Text("Add to Cart")
                                .fontWeight(.semibold)
                        }
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 14)
                    .background(isAdded ? Color.green : Color("EarthBrown"))
                    .foregroundColor(.white)
                    .clipShape(Capsule())
                    .shadow(color: Color.black.opacity(0.2), radius: 6, x: 0, y: 3)
                    .padding(.horizontal)
                }
                .padding(.bottom, 30)
            }
        }
        .navigationBarTitleDisplayMode(.inline)
    }
}
