function [C, sigma] = dataset3Params(X, y, Xval, yval)
%DATASET3PARAMS returns your choice of C and sigma for Part 3 of the exercise
%where you select the optimal (C, sigma) learning parameters to use for SVM
%with RBF kernel
%   [C, sigma] = DATASET3PARAMS(X, y, Xval, yval) returns your choice of C and 
%   sigma. You should complete this function to return the optimal C and 
%   sigma based on a cross-validation set.
%

% You need to return the following variables correctly.
F = [0.01; 0.03; 0.1; 0.3; 1; 3; 10; 30];
C = 1;
sigma = 0.3;
pred_error_combination = [];
counter = 1;

% ====================== YOUR CODE HERE ======================
% Instructions: Fill in this function to return the optimal C and sigma
%               learning parameters found using the cross validation set.
%               You can use svmPredict to predict the labels on the cross
%               validation set. For example, 
%                   predictions = svmPredict(model, Xval);
%               will return the predictions on the cross validation set.
%
%  Note: You can compute the prediction error using 
%        mean(double(predictions ~= yval))
%

for i=1:size(F, 1)
  for j=1:size(F, 1)
    C = F(i);
    sigma = F(j);
    model= svmTrain(X, y, C, @(x1, x2) gaussianKernel(x1, x2, sigma));;
    predictions = svmPredict(model, Xval);
    pred_error_combination(end+1, 1) = mean(double(predictions ~= yval));
    pred_error_combination(counter, 2) = C;
    pred_error_combination(counter, 3) = sigma;
    counter++;
  endfor
endfor

pred_error_combination
[error index] = min(pred_error_combination(:, 1))
C = pred_error_combination(index, 2)
sigma = pred_error_combination(index, 3)





% =========================================================================

end
