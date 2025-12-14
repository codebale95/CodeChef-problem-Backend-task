from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, Case, Vote
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer, CaseSerializer, VoteSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class LoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            return Response({
                'user': UserSerializer(user).data,
                'message': 'Login successful'
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_case(request):
    if request.user.role not in ['defendant', 'plaintiff']:
        return Response({'error': 'Only defendants and plaintiffs can submit cases'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = CaseSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(submitted_by=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_all_cases(request):
    cases = Case.objects.filter(status='approved')
    serializer = CaseSerializer(cases, many=True)
    return Response(serializer.data)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def edit_case(request, pk):
    if request.user.role != 'judge':
        return Response({'error': 'Only judges can edit cases'}, status=status.HTTP_403_FORBIDDEN)
    
    case = get_object_or_404(Case, pk=pk)
    serializer = CaseSerializer(case, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_case(request, pk):
    if request.user.role != 'judge':
        return Response({'error': 'Only judges can delete cases'}, status=status.HTTP_403_FORBIDDEN)
    
    case = get_object_or_404(Case, pk=pk)
    case.delete()
    return Response({'message': 'Case deleted'}, status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def vote_case(request, pk):
    if request.user.role != 'juror':
        return Response({'error': 'Only jurors can vote'}, status=status.HTTP_403_FORBIDDEN)

    case = get_object_or_404(Case, pk=pk)
    if case.status != 'approved':
        return Response({'error': 'Can only vote on approved cases'}, status=status.HTTP_400_BAD_REQUEST)

    if Vote.objects.filter(case=case, juror=request.user).exists():
        return Response({'error': 'You have already voted on this case'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = VoteSerializer(data={'case': pk, 'juror': request.user.id, 'verdict': request.data.get('verdict')})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Frontend Views
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        role = request.POST['role']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('signup')
        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        login(request, user)
        messages.success(request, 'Account created successfully')
        return redirect('dashboard')
    return render(request, 'signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    if request.method == 'POST':
        if 'title' in request.POST:  # Submit case
            if request.user.role not in ['defendant', 'plaintiff']:
                messages.error(request, 'Only defendants and plaintiffs can submit cases')
                return redirect('dashboard')
            title = request.POST['title']
            argument = request.POST['argument']
            evidence = request.POST.get('evidence', '')
            evidence_file = request.FILES.get('evidence_file')
            Case.objects.create(title=title, argument=argument, evidence=evidence, evidence_file=evidence_file, submitted_by=request.user)
            messages.success(request, 'Case submitted successfully')
            return redirect('dashboard')
        elif 'verdict' in request.POST:  # Vote
            case_id = request.POST['case_id']
            verdict = request.POST['verdict']
            case = get_object_or_404(Case, pk=case_id)
            if case.status != 'approved':
                messages.error(request, 'Can only vote on approved cases')
                return redirect('dashboard')
            if Vote.objects.filter(case=case, juror=request.user).exists():
                messages.error(request, 'You have already voted on this case')
                return redirect('dashboard')
            Vote.objects.create(case=case, juror=request.user, verdict=verdict)
            messages.success(request, 'Vote submitted')
            return redirect('dashboard')
        elif 'action' in request.POST:  # Judge actions
            case_id = request.POST['case_id']
            action = request.POST['action']
            case = get_object_or_404(Case, pk=case_id)
            if action == 'approve':
                case.status = 'approved'
                case.save()
                messages.success(request, 'Case approved')
            elif action == 'reject':
                case.status = 'rejected'
                case.save()
                messages.success(request, 'Case rejected')
            elif action == 'delete':
                case.delete()
                messages.success(request, 'Case deleted')
            return redirect('dashboard')

    cases = Case.objects.all()
    for case in cases:
        case.has_voted = case.votes.filter(juror=request.user).exists()
    return render(request, 'dashboard.html', {'cases': cases})

@login_required
def switch_role_view(request):
    if request.method == 'POST':
        role = request.POST['role']
        if role in ['juror', 'judge']:
            request.user.role = role
            request.user.save()
            messages.success(request, f'Role switched to {role}')
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def edit_case_view(request, pk):
    case = get_object_or_404(Case, pk=pk)
    if request.user.role != 'judge':
        messages.error(request, 'Only judges can edit cases')
        return redirect('dashboard')
    if request.method == 'POST':
        case.title = request.POST['title']
        case.argument = request.POST['argument']
        case.evidence = request.POST.get('evidence', '')
        if 'evidence_file' in request.FILES:
            case.evidence_file = request.FILES['evidence_file']
        case.save()
        messages.success(request, 'Case updated')
        return redirect('dashboard')
    return render(request, 'edit_case.html', {'case': case})
