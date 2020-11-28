function [J grad] = nnCostFunction(nn_params, ...
                                   input_layer_size, ...
                                   hidden_layer_size, ...
                                   num_labels, ...
                                   X, y, lambda)
%NNCOSTFUNCTION Implements the neural network cost function for a two layer
%neural network which performs classification
%   [J grad] = NNCOSTFUNCTON(nn_params, hidden_layer_size, num_labels, ...
%   X, y, lambda) computes the cost and gradient of the neural network. The
%   parameters for the neural network are "unrolled" into the vector
%   nn_params and need to be converted back into the weight matrices. 
% 
%   The returned parameter grad should be a "unrolled" vector of the
%   partial derivatives of the neural network.
%

% Reshape nn_params back into the parameters Theta1 and Theta2, the weight matrices
% for our 2 layer neural network
Theta1 = reshape(nn_params(1:hidden_layer_size * (input_layer_size + 1)), ...
                 hidden_layer_size, (input_layer_size + 1));

Theta2 = reshape(nn_params((1 + (hidden_layer_size * (input_layer_size + 1))):end), ...
                 num_labels, (hidden_layer_size + 1));

% Setup some useful variables
m = size(X, 1);
         
% You need to return the following variables correctly 
J = 0;
Theta1_grad = zeros(size(Theta1));
Theta2_grad = zeros(size(Theta2));

% ====================== YOUR CODE HERE ======================
% Instructions: You should complete the code by working through the
%               following parts.
%
% Part 1: Feedforward the neural network and return the cost in the
%         variable J. After implementing Part 1, you can verify that your
%         cost function computation is correct by verifying the cost
%         computed in ex4.m
%
% Part 2: Implement the backpropagation algorithm to compute the gradients
%         Theta1_grad and Theta2_grad. You should return the partial derivatives of
%         the cost function with respect to Theta1 and Theta2 in Theta1_grad and
%         Theta2_grad, respectively. After implementing Part 2, you can check
%         that your implementation is correct by running checkNNGradients
%
%         Note: The vector y passed into the function is a vector of labels
%               containing values from 1..K. You need to map this vector into a 
%               binary vector of 1's and 0's to be used with the neural network
%               cost function.
%
%         Hint: We recommend implementing backpropagation using a for-loop
%               over the training examples if you are implementing it for the 
%               first time.
%
% Part 3: Implement regularization with the cost function and gradients.
%
%         Hint: You can implement this around the code for
%               backpropagation. That is, you can compute the gradients for
%               the regularization separately and then add them to Theta1_grad
%               and Theta2_grad from Part 2.
% calculating h_theta(x):
X = [ones(m, 1) X];
N = sigmoid(X * Theta1');
N = [ones(m, 1) N];
% H is a 5000 * 10 (no of examples * no of labels)
% Each example has h_theta for all the nodes in the last layer where each node represents the probability(somehow) that it's the node to choose
H = sigmoid(N * Theta2');

a = repmat([1:num_labels], size(y), 1);
% y is a m*10 vector where each row represents 0s and 1 where 1 corresponds to the index of the digit being the output
y = (y == a);
% Out of each example, each label is checked against its hypothesis.
S=((-y) .* log(H)) ;
K=((1-y) .* log((1-H)));
J = 1/m * (sum(S(:)) - sum(K(:))) + (lambda/(2*m)) * (sum((Theta1(:, 2:end).^2)(:)) + sum((Theta2(:, 2:end).^2)(:))) ;

triangle1 = zeros(hidden_layer_size, input_layer_size + 1);
triangle2 = zeros(num_labels, hidden_layer_size + 1);

for t=1:m
  a1 = (X(t,:))';
  z2 = [1; (a1' * Theta1')'];
  a2 = [1;(sigmoid(a1' * Theta1'))'];
  z3 = (a2' * Theta2')';
  a3 = (sigmoid(a2' * Theta2'))';
 delta3 = a3 - (y(t, :))';
 delta2 = (Theta2' * delta3) .* sigmoidGradient(z2);
 delta2 = delta2(2:end); 
 triangle1 = triangle1 + (delta2 * (a1)');
 triangle2 = triangle2 + (delta3 * (a2)');
endfor

Theta1_grad = ((1/m) * triangle1) + [zeros(hidden_layer_size, 1) ((lambda/m) * Theta1)(:, 2:end)];
Theta2_grad = ((1/m) * triangle2) + [zeros(num_labels, 1) ((lambda/m) * Theta2)(:, 2:end)];















% -------------------------------------------------------------

% =========================================================================

% Unroll gradients
grad = [Theta1_grad(:) ; Theta2_grad(:)];


end
