import SwiftUI

struct FoodItem: Identifiable {
    let id = UUID()
    let name: String
    let imageName: String
    let score: String? // "High", "Medium", "Low"
}

struct DashboardView: View {
    @State private var query: String = ""

    let foodItems: [FoodItem] = [
        FoodItem(name: "Tofu", imageName: "tofu", score: "High"),
        FoodItem(name: "Chicken Breast", imageName: "chicken", score: "Medium"),
        FoodItem(name: "Cashews", imageName: "cashews", score: "Low"),
        FoodItem(name: "Nut Butter", imageName: "nutbutter", score: "Medium"),
        FoodItem(name: "Mushrooms", imageName: "mushrooms", score: "High")
    ]

    var filteredItems: [FoodItem] {
        if query.isEmpty {
            return foodItems
        } else {
            return foodItems.filter { $0.name.lowercased().contains(query.lowercased()) }
        }
    }

    var body: some View {
        NavigationView {
            ZStack {
                // Background gradient
                LinearGradient(
                    gradient: Gradient(colors: [Color("Cream"), Color("LeafGreen")]),
                    startPoint: .top,
                    endPoint: .bottom
                )
                .ignoresSafeArea()

                VStack(spacing: 0) {
                    // Search bar
                    HStack {
                        Image(systemName: "magnifyingglass")
                        TextField("Search", text: $query)
                            .textFieldStyle(PlainTextFieldStyle())
                        if !query.isEmpty {
                            Button(action: { query = "" }) {
                                Image(systemName: "xmark.circle.fill")
                                    .foregroundColor(.gray)
                            }
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                    .padding(.horizontal)
                    .padding(.top, 10)

                    // Section header
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Recommended for You")
                            .font(.title2)
                            .fontWeight(.bold)
                        Text("These are great eco-friendly items to start with.")
                            .font(.subheadline)
                            .foregroundColor(.gray)
                    }
                    .padding(.horizontal)
                    .padding(.top, 12)

                    // Item list
                    ScrollView(showsIndicators: true) {
                        LazyVStack(spacing: 12) {
                            ForEach(filteredItems) { item in
                                NavigationLink(destination: ProductDetailView(
                                    productName: item.name,
                                    imageName: item.imageName
                                )) {
                                    HStack(spacing: 12) {
                                        Image(item.imageName)
                                            .resizable()
                                            .scaledToFill()
                                            .frame(width: 60, height: 60)
                                            .clipShape(RoundedRectangle(cornerRadius: 10))
                                            .shadow(radius: 1)

                                        VStack(alignment: .leading, spacing: 2) {
                                            Text(item.name)
                                                .font(.subheadline)
                                                .foregroundColor(.primary)

                                            if let score = item.score {
                                                Text(score.uppercased())
                                                    .font(.caption2)
                                                    .fontWeight(.semibold)
                                                    .padding(.vertical, 2)
                                                    .padding(.horizontal, 8)
                                                    .background(scoreColor(for: score))
                                                    .foregroundColor(.white)
                                                    .clipShape(Capsule())
                                            }
                                        }

                                        Spacer()
                                    }
                                    .padding(10)
                                    .background(Color.white)
                                    .cornerRadius(12)
                                    .shadow(color: Color.black.opacity(0.05), radius: 2, x: 0, y: 1)
                                    .padding(.horizontal, 10)
                                }
                            }
                        }
                        .padding(.top, 8)
                    }
                }
            }
            .navigationTitle("EcoCart")
        }
    }

    func scoreColor(for score: String) -> Color {
        switch score.lowercased() {
        case "high": return .green
        case "medium": return .yellow
        case "low": return .red
        default: return .gray
        }
    }
}
