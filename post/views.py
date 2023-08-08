from django.shortcuts import render
from rest_framework import generics
from rest_framework import status


from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView

from .models import Post, PostLike, PostComment, CommentLike
from .serializers import PostSerializer, PostLikeSerializer, CommentSerializer, CommentLikeSerilazer
from shared.custom_pagination import CustomPagination
# Create your views here.
class ListApiView(generics.ListAPIView):
    serializer_class = PostSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        return Post.objects.all()

class PostCreateApiVew(generics.CreateAPIView):

    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated, ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class RetieveUpdateDestroyApiView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, ]

    def put(self, request, *args, **kwargs):
        post = self.get_object()
        serializer = PostSerializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {
                'success': True,
                'status': status.HTTP_200_OK,
                "message": 'successfuly updated',
                'data': serializer.data
                }
        )
    def delete(self, request, *args, **kwargs):
        post = self.get_object()
        post.delete()

        return Response(
            {
                'success': True,
                'status': status.HTTP_204_NO_CONTENT,
                "message": 'successfuly deleted',

                }
        )

class PostCommentListView(generics.ListAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny,]

    def get_queryset(self):
        post_id=self.kwargs['pk']
        queryset=PostComment.objects.filter(post__id=post_id)
        return queryset

# class CommentCreateView(generics.CreateAPIView):
#     serializer_class = CommentSerializer
#     permission_classes = [IsAuthenticated,]
#
#
#     def perform_create(self, serializer):
#         post_id=self.kwargs['pk']
#         serializer.save(author=self.request.user,post_id=post_id)

class CommentListCreateApiView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly,]
    serializer_class = CommentSerializer
    queryset = PostComment.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostLikeListView(generics.ListAPIView):
    permission_classes = [AllowAny,]
    serializer_class = PostLikeSerializer

    def get_queryset(self):
        post_id=self.kwargs['pk']
        return PostLike.objects.filter(post_id=post_id)

class CommentRetrieveView(generics.RetrieveAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny,]
    queryset = PostComment.objects.all()

class CommentLikeListView(generics.ListAPIView):

    serializer_class = CommentLikeSerilazer
    permission_classes = [AllowAny,]
    queryset = CommentLike.objects.all()

class PostLikeListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly,]
    serializer_class = PostLikeSerializer
    queryset = PostLike.objects.all()
    pagination_class = CustomPagination

    def perform_create(self, serializer):

        serializer.save(author=self.request.user)

class PostLikeDestroyView(generics.RetrieveDestroyAPIView):
    serializer_class = PostLikeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly,]
    queryset = PostLike.objects.all()

    def delete(self, request, *args, **kwargs):
        like = self.get_object()
        like.delete()

        return Response(
            {
                'success': True,
                'status': status.HTTP_204_NO_CONTENT,
                "message": 'successfuly deleted',

                }
        )
class PostLikeView(APIView):

    def post(self,request,pk):
        try:
            post_like=PostLike.objects.get(author=self.request.user,post_id=pk)

            post_like.delete()
            data = {
                    'success':True,
                    "message":'You deleted this post',

               }
            return Response(data)
        except PostLike.DoesNotExist:
            post_like=PostLike.objects.create(author=self.request.user,post_id=pk)
            data = {
                'success': True,
                "message": 'You liked this post',


            }
            return Response(data)





    # def post(self,request,pk):
    #     try:
    #         post_like=PostLike.objects.create(author=self.request.user,post_id=pk)
    #
    #         serializer=PostLikeSerializer(post_like)
    #         data={
    #             'success':True,
    #             "message":'You liked this post',
    #             "data":serializer.data
    #
    #         }
    #         return Response(data)
    #     except Exception as e:
    #
    #         data = {
    #             'success': False,
    #             "message": f"{str(e)}",
    #             "data": None
    #
    #         }
    #         return Response(data)
    #
    # def delete(self,request,pk):
    #     try:
    #         post_like=PostLike.objects.get(author=self.request.user,post_id=pk)
    #         post_like.delete()
    #         return Response(
    #             {
    #                 'success': True,
    #                 'status': status.HTTP_204_NO_CONTENT,
    #                 "message": 'successfuly deleted',
    #
    #             }
    #         )
    #     except Exception as e:
    #         return Response(
    #             {
    #                 'success': False,
    #                 'status': status.HTTP_400_BAD_REQUEST,
    #                 "message": f"{str(e)}",
    #
    #             }
    #         )

# class CommentLikeView(APIView):
#
#     def post(self,request,pk):
#         try:
#             post_comment = CommentLike.objects.create(author=self.request.user,comment_id=pk)
#
#             serializer=CommentLikeSerilazer(post_comment)
#             data={
#                 'success':True,
#                 "message":'You liked this comment',
#                 "data":serializer.data
#
#             }
#             return Response(data)
#         except Exception as e:
#
#             data = {
#                 'success': False,
#                 "message": f"{str(e)}",
#                 "data": None
#
#             }
#             return Response(data)
#
#     def delete(self,request,pk):
#         try:
#             comment_like=CommentLike.objects.get(author=self.request.user,comment_id=pk)
#             comment_like.delete()
#             return Response(
#                 {
#                     'success': True,
#                     'status': status.HTTP_204_NO_CONTENT,
#                     "message": 'successfuly deleted',
#
#                 }
#             )
#         except Exception as e:
#             return Response(
#                 {
#                     'success': False,
#                     'status': status.HTTP_400_BAD_REQUEST,
#                     "message": f"{str(e)}",
#
#                 }
#             )


class CommentLikeView(APIView):
    def post(self,request,pk):
        try:
            comment_like=CommentLike.objects.get(author=self.request.user,comment_id=pk)

            comment_like.delete()
            return Response(
                {
                'success': True,
                'status': status.HTTP_204_NO_CONTENT,
                "message": 'your comment_like successfuly deleted',

                }
            )
        except CommentLike.DoesNotExist:
            comment_like=CommentLike.objects.create(author=self.request.user,comment_id=pk)
            return Response(
                {
                    'success': True,
                    'message': "you liked this comment",
                    "status":status.HTTP_201_CREATED,

                }
            )






