from django.urls import path

from post.views import ListApiView, PostCreateApiVew, RetieveUpdateDestroyApiView,\
 PostCommentListView,CommentListCreateApiView,PostLikeListView,CommentRetrieveView,\
CommentLikeListView,PostLikeListCreateView,PostLikeDestroyView,PostLikeView,CommentLikeView

urlpatterns = [
    path('list/', ListApiView.as_view()),
    path('create/', PostCreateApiVew.as_view()),
    path('<uuid:pk>/', RetieveUpdateDestroyApiView.as_view()),
    path('<uuid:pk>/comments/', PostCommentListView.as_view()),
    # path('<uuid:pk>/comments/create/', CommentCreateView.as_view()),
    path('comments/create/',CommentListCreateApiView.as_view()),
    path('<uuid:pk>/likes/',PostLikeListView.as_view()),
    path('comments/<uuid:pk>/',CommentRetrieveView.as_view()),
    path('comments/<uuid:pk>/likes/',CommentLikeListView.as_view()),
    path('likes/create/',PostLikeListCreateView.as_view()),
    path('likes/<uuid:pk>/delete/',PostLikeDestroyView.as_view()),
    path('<uuid:pk>/create-delete-like/',PostLikeView.as_view()),
    path('<uuid:pk>/create-delete-comment_like/',CommentLikeView.as_view())

 ]