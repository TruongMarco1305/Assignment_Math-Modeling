Author: Tran Bao Phuc Long - 2352703 & Nguyen Thanh Hieu - 2352331

GREEDY HEURISTIC APPROACH TO REAL WORLD TWO-DIMENSIONAL CUTTING PROBLEMS

In the study "*Approaches to Real World Two-Dimensional Cutting Problems*" by Enrico Malaguti, Rosa Medina Durán, and Paolo Toth, heuristic methods are highlighted as essential for tackling complex 2D cutting stock problems efficiently. These approaches are designed to provide good, near-optimal solutions quickly, making them ideal for large-scale or variable industrial applications where exact methods may be too slow or impractical. The study explores various heuristics, such as greedy and local search algorithms, which can be adapted to specific real-world requirements, ensuring effective material utilization and reduced waste. In this section, we will delve further into the **greedy heuristic approach**, explore its advantages and disadvantages, also provide an application context for this approach. 

### **Algorithm Overview**
A heuristic approach in optimization is a rule-based method that aims to find a "good enough" solution within a reasonable time frame. Unlike exact algorithms that search exhaustively for the best solution, greedy heuristics prioritizes local optimality, often sorting elements by criteria such as size or value and making selections that maximize short-term gain. This can be described as following:
1. **Product Sorting**: Prioritizes products based on size or shape. Larger products are often placed first to reduce large, irregular gaps.
2. **Greedy Placement**: Uses a local optimization strategy by placing items in the "best" current spot, defined by criteria like minimal waste or proximity to edges.
3. **Waste Minimization**: Evaluates possible placements and chooses the one that leaves the least amount of unused stock.
*Note that, we only count something as a waste if that is the redundant of a used stock, any other unused ones will not be considered.*

### **Advantages**
1. **Simplicity and Ease of Implementation**: Greedy algorithms are straightforward to design and implement, often requiring minimal code compared to more complex optimization methods.
2. **Low Computational Cost**: These algorithms usually have a lower computational overhead compared to exact algorithms, making them effective for small to medium-sized instances or real-time decision-making.
3. **Adaptability**: Greedy strategies can be adapted and customized to various specific use cases by altering selection criteria or adding constraints (e.g., minimizing waste, maximizing production).
4. **Reasonable Quality Solutions**: Although not guaranteed to be optimal, greedy heuristics often yield good or acceptable solutions that are sufficient for practical applications.
5. **Usefulness in Problem Approximation**: Greedy heuristics can be a good starting point for finding an initial solution that can be refined further with more sophisticated techniques.

### **Disadvantages**
1. **Lack of Global Optimality**: Greedy algorithms focus on local optimal choices at each step, which can lead to suboptimal global solutions. They do not guarantee the best possible outcome.
2. **Potential for Inconsistency**: Heuristic solutions can vary depending on initial conditions, randomization, or specific implementation details, which may lead to inconsistent results in some scenarios.
3. **Limited Flexibility**: Greedy algorithms are generally tailored to specific criteria for optimization and may not handle multiple objectives well without significant modifications.

### **Optimal application contexts**
Greedy heuristics perform best under the following conditions:
1. **Greedy-Choice Property**: The problem must allow for locally optimal choices to lead to a global optimal solution, ensuring that selecting the best immediate option at each step results in the best overall outcome.
2. **Defined Selection Criterion**: The algorithm should have a clear and simple rule for making decisions at each step (e.g., choosing the next item with the highest value-to-weight ratio).
3. **Simple, Clear Objectives**: Problems with straightforward, quantifiable goals, such as maximizing profit or minimizing cost, are more suitable for greedy approaches.
4. **Homogeneous Input Structure**: Problems where the input elements contribute similarly or have minimal variability make greedy solutions more effective and comparable to more complex algorithms.

### **Conclusion**
In conclusion, greedy heuristics are valuable tools in optimization due to their simplicity, speed, and ability to provide reasonably good solutions quickly. They are especially useful for large-scale problems where exact algorithms may be impractical. However, their main drawbacks include a lack of global optimality and susceptibility to suboptimal decisions, making them less suitable for problems that require more comprehensive, strategic approaches. Despite these limitations, greedy heuristics remain a practical choice in situations where rapid, decent solutions are needed and perfect optimality is not crucial.

### **Reference**
Enrico Malaguti, Rosa Medina Durán, Paolo Toth, "Approaches to real world two-dimensional cutting problems",
*Omega*, Volume 47, 2014, Pages 99-115.
