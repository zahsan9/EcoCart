import SwiftUI

struct MealPrepView: View {
    var body: some View {
        VStack(spacing: 30) {
            // Spacer for top padding
            Spacer().frame(height: 40)

            // Top buttons
            HStack(spacing: 20) {
                Button(action: {
                    print("Random meal plan requested")
                }) {
                    Text("Random")
                        .fontWeight(.semibold)
                        .padding(.vertical, 12)
                        .padding(.horizontal, 28)
                        .background(Color("LeafGreen"))
                        .foregroundColor(.white)
                        .clipShape(Capsule())
                        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 4)
                }

                Button(action: {
                    print("Using cart to generate plan")
                }) {
                    Text("Use Cart")
                        .fontWeight(.semibold)
                        .padding(.vertical, 12)
                        .padding(.horizontal, 28)
                        .background(Color("EarthBrown"))
                        .foregroundColor(.white)
                        .clipShape(Capsule())
                        .shadow(color: Color.black.opacity(0.1), radius: 5, x: 0, y: 4)
                }
            }

            // Main title + subtitle
            VStack(spacing: 8) {
                Text("Meal Prep")
                    .font(.system(size: 36, weight: .bold, design: .rounded))
                    .foregroundColor(Color("EarthBrown"))

                Text("AI-powered recipe guide")
                    .font(.subheadline)
                    .foregroundColor(.gray)
            }

            Spacer()
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .background(
            LinearGradient(
                gradient: Gradient(colors: [Color("Cream"), Color("LeafGreen")]),
                startPoint: .top,
                endPoint: .bottom
            )
            .ignoresSafeArea()
        )
    }
}
